"""E11 PILOTO C3/C4 EM NOVA BANCADA. Sem --execute, apenas planejamento.

NAO aplica YAML. --execute faz UM snapshot e UMA carga: nao repetir em falhas.
"""
import argparse
import base64
import gzip
import json
from pathlib import Path
import re
import subprocess
import sys
import threading

from benchmark import collector
from benchmark.campaign_controls import final_readonly_cold_check
from benchmark.environment_snapshot import capture_environment
from benchmark.runtime_gate import assess_capacity, capture_effective_quotas
from benchmark.campaign_exclusivity import check_exclusivity_readonly
from benchmark.ownership import capture_kind_ownership
from benchmark.measurement_profile import (
    TIMING_ONLY, RESOURCES_DIAGNOSTIC, MODES, select_sampler, profile_record,
    not_collected_quality, require_new_timing_identity,
)
from benchmark.evidence import archive, check_run, write_json, write_jsonl, write_csv, hash_file
from benchmark.resource_contract import verify_kube_resources
from benchmark.fixtures import characterize, generate, rebase
from benchmark.prepare import namespace_for
from c0.io import read_jsonl, validate_input
from c0.oracle import calculate_expected_effects
from c3 import runner as kube

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = "kind-tcc2-pon"
ROLES = ("attribute-source", "logic-engine", "rule-executor")
SEEDS = {100: 20260501, 1000: 20260502, 10000: 20260503}
NODES = ("tcc2-pon-worker", "tcc2-pon-control-plane")


def command(*args, stdin=None, timeout=120):
    return subprocess.run([str(x) for x in args], input=stdin, cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, check=False)


def kubedata(namespace, *args):
    proc = command("kubectl", "--context", CONTEXT, "-n", namespace, *args)
    if proc.returncode:
        raise RuntimeError(f"kubectl falhou: {proc.stderr[-400:]}")
    return json.loads(proc.stdout)


def ensure_safe(scenario, label, run_id, rows):
    namespace = namespace_for(scenario, label)
    if not re.fullmatch(r"e11-[a-z0-9-]{4,48}", run_id):
        raise ValueError("run_id precisa iniciar e11- e ser exclusivo")
    if len(rows) not in SEEDS:
        raise ValueError("tamanho da fixture fora da matriz E11")
    n, seed = len(rows), SEEDS[len(rows)]
    canonical_id = f"e11-canonical-{n}-{seed}"
    if validate_input(rows) != (canonical_id, seed) or rows != generate(n, seed, canonical_id):
        raise ValueError("fixture nao corresponde byte-semanticamente a geracao canonica E11")
    return namespace


def configure(scenario, namespace, run_id):
    kube.NS = namespace
    kube.RUN_ID = run_id
    kube.SCENARIO = scenario


def preflight(scenario, namespace):
    if kube.command("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("branch Git incorreta")
    if kube.command("git", "status", "--porcelain").strip():
        raise ValueError("Git com alteracoes locais")
    kube.command("git", "diff", "--quiet", kube.BUILD_SHA, "HEAD",
                 "--", "pon", "c1", "Dockerfile", ".dockerignore")
    image = json.loads(kube.command("docker", "image", "inspect", kube.IMAGE))[0]
    if image["Id"] != kube.IMAGE_ID:
        raise ValueError("imagem Docker divergente")
    top = kube.topology()
    wanted = {"attribute-source": "tcc2-pon-worker",
              "logic-engine": "tcc2-pon-worker" if scenario == "C3" else "tcc2-pon-control-plane",
              "rule-executor": "tcc2-pon-worker"}
    if {role: top["pods"][role]["node"] for role in ROLES} != wanted:
        raise ValueError("agendamento da aplicacao divergente")
    clients = kubedata(namespace, "get", "pods", "-l",
                       "app=e11-benchmark-client", "-o", "json")["items"]
    if len(clients) != 1:
        raise ValueError("bancada sem um unico Pod cliente")
    pod = clients[0]
    stats = pod.get("status", {}).get("containerStatuses") or []
    if (pod.get("status", {}).get("phase") != "Running"
            or pod["spec"].get("nodeName") != "tcc2-pon-worker"
            or len(stats) != 1 or stats[0].get("restartCount") != 0
            or stats[0].get("ready") is not True
            or pod["spec"]["containers"][0].get("image") != kube.IMAGE):
        raise ValueError("Pod cliente inesperado")
    top["resource_contract"] = verify_kube_resources(top, pod)
    source = top["pods"]["attribute-source"]["name"]
    cold = {}
    for role in ROLES:
        status, cold[role] = kube.http(source, role, "/state")
        logs = kube.read_logs(top["pods"][role]["name"])
        if status != 200 or cold[role].get("ready") is not False or cold[role].get("run_id") is not None:
            raise ValueError(f"{role} nao esta frio")
        if any(x.get("event_type") == "mutation" for x in logs):
            raise ValueError(f"{role} ja recebeu mutacoes")
    if cold["attribute-source"].get("attributes") != {"atA": 0, "atB": 0}:
        raise ValueError("atributos iniciais divergentes")
    return top, pod["metadata"]["name"], source, cold


def client_program(rows):
    payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n"
                      for row in rows)
    packed = base64.b64encode(gzip.compress(payload.encode("utf-8"))).decode("ascii")
    prefix = ("import sys,io,gzip,base64\n"
              f"sys.stdin=io.StringIO(gzip.decompress(base64.b64decode('{packed}')).decode('utf-8'))\n")
    return prefix + (ROOT / "benchmark" / "client.py").read_text(encoding="utf-8")


def call_batch(namespace, pod, rows, timeout_per_request, batch_timeout):
    return command("kubectl", "--context", CONTEXT, "-n", namespace,
                   "exec", "-i", pod, "--", "python", "-",
                   "--url", "http://attribute-source:8080",
                   "--timeout", str(timeout_per_request),
                   stdin=client_program(rows), timeout=batch_timeout)


class Sampler:
    def __init__(self, namespace, period):
        self.namespace, self.period = namespace, period
        self.samples, self.errors = [], []
        self.done = threading.Event()
        self.worker = threading.Thread(target=self.collect, daemon=True)

    def collect(self):
        while not self.done.is_set():
            try:
                self.samples.extend(collector.capture(CONTEXT, self.namespace, NODES))
            except Exception as exc:
                self.errors.append(str(exc))
            self.done.wait(self.period)

    def prime(self):
        """Coleta linha de base ainda antes de iniciar o cliente de carga."""
        try:
            self.samples.extend(collector.capture(CONTEXT, self.namespace, NODES))
        except Exception as exc:
            self.errors.append(f"baseline: {exc}")

    def start(self):
        self.worker.start()

    def stop(self):
        self.done.set()
        self.worker.join(timeout=30)
        if self.worker.is_alive():
            self.errors.append("sampler nao encerrou")
        try:
            self.samples.extend(collector.capture(CONTEXT, self.namespace, NODES))
        except Exception as exc:
            self.errors.append(str(exc))


def transport_checks(top, rows, logs, states):
    source, logic, executor = (logs[r] for r in ROLES)
    attr_sent = [e["payload"] for e in source if e.get("event_type") == "send"
                 and e.get("path") == "/notifications/attribute"]
    attr_recv = [e["payload"] for e in logic if e.get("event_type") == "mutation"
                 and e.get("path") == "/notifications/attribute" and e.get("status") == 200]
    cond_sent = [e["payload"] for e in logic if e.get("event_type") == "send"
                 and e.get("path") == "/notifications/condition"]
    cond_recv = [e["payload"] for e in executor if e.get("event_type") == "mutation"
                 and e.get("path") == "/notifications/condition" and e.get("status") == 200]
    counts = characterize(rows)
    return {
        "attribute_causality": attr_sent == attr_recv
                               and len(attr_sent) == counts["changed"],
        "condition_causality": cond_sent == cond_recv
                               and len(cond_sent) == counts["condition_transitions"],
        "effects_logged": [e["payload"] for e in executor
                           if e.get("event_type") == "effect"] == states["rule-executor"]["effects"],
        "pods_stable": top["pods"] == kube.topology()["pods"],
    }


def run(args, rows, namespace):
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    report = {"status": "FAIL", "stage": "preflight", "scenario": args.scenario,
              "namespace": namespace, "run_id": args.run_id,
              "started_snapshot": False, "started_changes": False}
    source_pod = None
    try:
        configure(args.scenario, namespace, args.run_id)
        rebased = rebase(rows, args.run_id)
        expected = calculate_expected_effects(rebased)
        write_jsonl(output / "inputs.jsonl", rebased)
        write_jsonl(output / "expected.jsonl", expected)
        write_json(output / "manifest.json", {
            "scenario": args.scenario, "run_id": args.run_id, "namespace": namespace,
            "load": len(rows), "seed": rows[0]["seed"],
            "canonical_input_sha256": hash_file(args.fixture),
            "git_sha": kube.git_sha(), "image": kube.IMAGE, "image_id": kube.IMAGE_ID,
            "clock": "perf_counter_ns (Pod cliente), HTTP/1.0",
            "timeout_per_request_s": args.timeout,
            "batch_timeout_s": args.batch_timeout,
            "sample_period_s": args.period,
            **profile_record(args.measurement_mode),
            "scientific_status": "E11-M00B_PREPARED; protocolo ainda nao congelado",
        })
        top, client_pod, source_pod, cold = preflight(args.scenario, namespace)
        write_json(output / "topology-start.json", {
            "pods": top["pods"], "nodes": top["nodes"], "services": top["services"],
            "client_pod": client_pod})
        write_json(output / "states-cold.json", cold)
        write_json(output / "resource-contract.json", top["resource_contract"])
        if args.measurement_mode == TIMING_ONLY:
            ownership = capture_kind_ownership(
                args.scenario, args.label, args.run_id,
                lambda *argv: kube.command(*argv))
            write_json(output / "ownership-start.json", ownership)
            exclusive = check_exclusivity_readonly(
                args.scenario, namespace, lambda *argv: kube.command(*argv))
            write_json(output / "campaign-exclusivity.json", exclusive)
            environment = capture_environment(args.scenario, args.run_id)
            write_json(output / "environment.json", environment)
            capacity_gate = assess_capacity(environment)
            write_json(output / "capacity-gate.json", capacity_gate)

            def get_status_body(role, path):
                code, payload = kube.http(source_pod, role, path)
                if code != 200:
                    raise ValueError(f"{role}: GET {path} HTTP inesperado {code}")
                return payload

            uniform = final_readonly_cold_check(
                lambda role: get_status_body(role, "/health/live"),
                lambda role: get_status_body(role, "/state"),
                lambda role: kube.read_logs(top["pods"][role]["name"]))
            write_json(output / "preflight-uniform.json", uniform)
            pods_by_role = {role: top["pods"][role]["name"] for role in ROLES}
            pods_by_role["client"] = client_pod
            quotas = capture_effective_quotas(
                args.scenario, namespace=namespace, pods=pods_by_role,
                query=lambda *argv: kube.command(*argv))
            write_json(output / "effective-quotas.json", quotas)
        report["stage"] = "snapshot"
        report["started_snapshot"] = True
        status, reply = kube.http(source_pod, "attribute-source",
                                  "/init/snapshot", {"run_id": args.run_id})
        write_json(output / "snapshot-response.json", {"http_status": status, "body": reply})
        if (status != 200 or reply.get("duplicate") is not False
                or reply.get("ready") is not True):
            raise ValueError("snapshot divergente; NAO repetir")
        initial = {r: kube.http(source_pod, r, "/state")[1] for r in ROLES}
        write_json(output / "states-after-snapshot.json", initial)
        if not all(s.get("ready") is True and s.get("run_id") == args.run_id
                   for s in initial.values()):
            raise ValueError("snapshot nao confirmado 3/3")
        if initial["rule-executor"].get("effects"):
            raise ValueError("efeitos antes de iniciar carga")
        report["stage"] = "batch"
        monitor = select_sampler(
            args.measurement_mode, lambda: Sampler(namespace, args.period))
        write_json(output / "metrics-status.json", profile_record(args.measurement_mode))
        if monitor is not None:
            monitor.prime()
            monitor.start()
        try:
            report["started_changes"] = True
            try:
                proc = call_batch(namespace, client_pod, rebased, args.timeout, args.batch_timeout)
            except subprocess.TimeoutExpired as exc:
                # O resultado de kubectl exec e incerto: preservar os bytes recebidos
                # e NUNCA repetir o POST nem reiniciar o Pod para obter mais dados.
                for filename, raw in (
                    ("client.stdout.partial.log", exc.stdout),
                    ("client.stderr.partial.log", exc.stderr),
                ):
                    if isinstance(raw, bytes):
                        raw = raw.decode("utf-8", errors="replace")
                    (output / filename).write_text(raw or "", encoding="utf-8")
                raise RuntimeError("timeout do lote; estado remoto indeterminado; NAO repetir") from exc
            (output / "client.stderr.log").write_text(proc.stderr, encoding="utf-8")
            (output / "client.stdout.jsonl").write_text(proc.stdout, encoding="utf-8")
        finally:
            if monitor is not None:
                # Telemetria somente no modo diagnostico.
                monitor.stop()
                write_jsonl(output / "metrics-samples.jsonl", monitor.samples)
                write_csv(output / "metrics-samples.csv", monitor.samples,
                          ("retrieved_utc", "collector_seconds", "node", "namespace",
                           "pod", "pod_uid", "container", "cpu_time_utc",
                           "cpu_usage_core_ns", "memory_time_utc",
                           "memory_working_set_bytes", "network_rx_bytes_pod",
                           "network_tx_bytes_pod", "network_interfaces"))
                write_json(output / "metrics-errors.json", monitor.errors)
        records = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
        if proc.returncode or not records or records[-1].get("status") != "PASS":
            raise ValueError(f"cliente falhou exit={proc.returncode}; NAO repetir")
        write_json(output / "batch-summary.json", records[-1])
        write_csv(output / "requests.csv", [
            {"step": x.get("step"), "duration_ns": x.get("duration_ns"),
             "status": x.get("status"),
             "changed": (x.get("response") or {}).get("changed")}
            for x in records[:-1]],
            ("step", "duration_ns", "status", "changed"))
        after = kube.topology()
        write_json(output / "topology-end.json", {
            "pods": after["pods"], "nodes": after["nodes"], "services": after["services"]})
        final = {r: kube.http(source_pod, r, "/state")[1] for r in ROLES}
        write_json(output / "states-final.json", final)
        write_jsonl(output / "effects.jsonl", final["rule-executor"]["effects"])
        logs = {r: kube.read_logs(after["pods"][r]["name"]) for r in ROLES}
        for role in ROLES:
            write_jsonl(output / f"{role}-logs.jsonl", logs[role])
        validated = check_run(rebased, records, final)
        validated["transport"] = transport_checks(top, rebased, logs, final)
        if monitor is not None:
            validated["metric_quality"] = collector.quality(
                monitor.samples, {r: (top["pods"][r]["uid"], r) for r in ROLES},
                batch=records[-1], collection_errors=monitor.errors)
        else:
            validated["metric_quality"] = not_collected_quality()
        validated["status"] = ("PASS" if validated["status"] == "PASS"
                               and all(validated["transport"].values()) else "FAIL")
        report["validation"] = validated
        report["status"], report["stage"] = validated["status"], "complete"
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        if source_pod:
            try:
                states = {r: kube.http(source_pod, r, "/state")[1] for r in ROLES}
                write_json(output / "states-recovery.json", states)
            except Exception as e:
                report["recovery_error"] = str(e)
            try:
                topo = kube.topology()
                write_json(output / "topology-recovery.json", {
                    "pods": topo["pods"], "nodes": topo["nodes"],
                    "services": topo["services"]})
                for role in ROLES:
                    try:
                        write_jsonl(output / f"{role}-logs-recovery.jsonl",
                                    kube.read_logs(topo["pods"][role]["name"]))
                    except Exception as log_exc:
                        (output / f"{role}-logs-recovery-error.txt").write_text(
                            str(log_exc) + "\n", encoding="utf-8")
            except Exception as topo_exc:
                report["topology_recovery_error"] = str(topo_exc)
    finally:
        write_json(output / "validation.json", report)
        zipped = archive(output)
        print("STATUS:", report["status"], flush=True)
        print("ETAPA:", report["stage"], flush=True)
        print("ZIP:", zipped["zip"], flush=True)
        print("ZIP_SHA256:", zipped["sha256"], flush=True)
        if report["status"] != "PASS":
            print("NAO REPETIR: pode haver mutacao parcial, preservar evidencias.", flush=True)
    return report["status"] == "PASS"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=["C3", "C4"], required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--batch-timeout", type=int, default=600)
    parser.add_argument("--period", type=float, default=1)
    parser.add_argument("--measurement-mode", choices=MODES,
                        default=RESOURCES_DIAGNOSTIC,
                        help="timing_only: sem sonda; resources_diagnostic: modo legado")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if not 0.1 <= args.period <= 15 or not 1 <= args.timeout <= 120 or not 10 <= args.batch_timeout <= 3600:
        parser.error("time-outs/periodo invalidos")
    rows = read_jsonl(args.fixture)
    require_new_timing_identity(args.measurement_mode, args.scenario,
                                args.label, args.run_id)
    ns = ensure_safe(args.scenario, args.label, args.run_id, rows)
    if not args.execute:
        print(json.dumps({"status": "PLAN_ONLY", "scenario": args.scenario,
                          "namespace": ns, "run_id": args.run_id,
                          "rows": len(rows), "fixture": str(args.fixture),
                          "expected": characterize(rebase(rows, args.run_id)),
                          **profile_record(args.measurement_mode),
                          "execute": False}, indent=2, ensure_ascii=False))
        return 0
    return 0 if run(args, rows, ns) else 2


if __name__ == "__main__":
    sys.exit(main())
