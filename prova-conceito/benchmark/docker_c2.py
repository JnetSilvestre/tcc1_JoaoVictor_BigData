"""Piloto C2 em REDE/CONTEINERES NOVOS. Sem --execute, apenas plano.

O --execute e MUTANTE: snapshot e lote UNICOS. Em falha, preservar tudo;
NAO usar docker rm, restart, compose down ou network rm automaticamente.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

from benchmark.evidence import archive, check_run, hash_file, write_csv, write_json, write_jsonl
from benchmark.fixtures import characterize, generate, rebase
from benchmark.runner import client_program
from c0.io import read_jsonl, validate_input
from c0.oracle import calculate_expected_effects
from c2.runner import HTTP_CLIENT, IMAGE_TAG, BUILD_SHA

ROOT = Path(__file__).resolve().parents[1]
IMAGE_ID = "sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a"
ROLES = ("attribute-source", "logic-engine", "rule-executor")
NEXT_ROLE = {"attribute-source": "logic-engine", "logic-engine": "rule-executor"}
MEM_APP = 256 * 1024 * 1024
MEM_CLIENT = 128 * 1024 * 1024
CPU_LIMIT = "0.5"
SEEDS = {100: 20260501, 1000: 20260502, 10000: 20260503}
RESOURCE_SCRIPT = """import json,pathlib,datetime
root=pathlib.Path('/sys/fs/cgroup')
cpu={}
for line in (root/'cpu.stat').read_text().splitlines():
 k,_,v=line.partition(' ')
 if v.strip().isdigit(): cpu[k]=int(v)
def read(name):
 try: return int((root/name).read_text().strip())
 except (FileNotFoundError,PermissionError,ValueError): return None
print(json.dumps({'cpu_usage_usec':cpu.get('usage_usec'),
 'cpu_nr_throttled':cpu.get('nr_throttled'),
 'cpu_throttled_usec':cpu.get('throttled_usec'),
 'memory_current_bytes':read('memory.current'),
 'memory_peak_lifetime_bytes':read('memory.peak'),
 'capture_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
"""


def command(*args, stdin=None, timeout=120):
    return subprocess.run([str(x) for x in args], input=stdin, cwd=ROOT,
                          capture_output=True, text=True, errors="replace",
                          encoding="utf-8", timeout=timeout, check=False)


def checked(*args, stdin=None, timeout=120):
    result = command(*args, stdin=stdin, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"comando falhou ({result.returncode}): {args[:5]!r}, "
                           f"stderr={result.stderr[-500:]}")
    return result.stdout


def identities(label):
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,20}[a-z0-9])?", label):
        raise ValueError("label DNS curta invalida")
    network = f"tcc2-pon-e11-c2-{label}"
    return network, {r: f"{network}-{r}" for r in ROLES} | {
        "client": f"{network}-benchmark-client"}


def validate_fixture(label, run_id, rows):
    network, names = identities(label)
    if not re.fullmatch(r"e11-c2-[a-z0-9-]{4,48}", run_id):
        raise ValueError("run_id deve ser novo, e11-c2-...")
    if len(rows) not in SEEDS:
        raise ValueError("tamanho nao aprovado")
    n, seed = len(rows), SEEDS[len(rows)]
    canon = f"e11-canonical-{n}-{seed}"
    if validate_input(rows) != (canon, seed) or rows != generate(n, seed, canon):
        raise ValueError("fixture difere da fonte canonica E11")
    return network, names


def build_service_command(role, name, network):
    cmd = ["docker", "run", "-d", "--name", name,
           "--network", network, "--network-alias", role,
           "--cpus", CPU_LIMIT, "--memory", str(MEM_APP),
           "--memory-swap", str(MEM_APP),
           "--label", "tcc2.e11=pilot", IMAGE_TAG,
           role, "--port", "8080", "--listen-host", "0.0.0.0"]
    if role in NEXT_ROLE:
        cmd += ["--downstream-host", NEXT_ROLE[role], "--downstream-port", "8080"]
    return cmd


def build_client_command(name, network):
    return ["docker", "run", "-d", "--name", name,
            "--network", network, "--network-alias", "e11-benchmark-client",
            "--cpus", CPU_LIMIT, "--memory", str(MEM_CLIENT),
            "--memory-swap", str(MEM_CLIENT),
            "--label", "tcc2.e11=pilot",
            "--entrypoint", "python", IMAGE_TAG,
            "-c", "import time; time.sleep(86400)"]


def preflight(network, names):
    if checked("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("branch de trabalho incorreta")
    if checked("git", "status", "--porcelain").strip():
        raise ValueError("Git nao esta limpo")
    delta = command("git", "diff", "--quiet", BUILD_SHA, "HEAD", "--",
                    "pon", "c1", "Dockerfile", ".dockerignore")
    if delta.returncode:
        raise ValueError("codigo funcional alterado desde imagem aprovada")
    image = json.loads(checked("docker", "image", "inspect", IMAGE_TAG))[0]
    if image.get("Id") != IMAGE_ID:
        raise ValueError("imagem Docker divergente da C2 aprovada")
    if image.get("Os") != "linux" or image.get("Architecture") != "amd64":
        raise ValueError("imagem nao e linux/amd64")
    existing_nets = checked("docker", "network", "ls", "--format", "{{.Name}}").splitlines()
    existing_containers = checked("docker", "ps", "-a", "--format", "{{.Names}}").splitlines()
    if network in existing_nets or any(n in existing_containers for n in names.values()):
        raise ValueError("bancada ja existe: NAO reutilizar nomes")
    return {"git_sha": checked("git", "rev-parse", "HEAD").strip(),
            "image_id": image["Id"], "network": network,
            "resources_app": {"cpu_limit": 0.5, "memory_limit_bytes": MEM_APP,
                              "memory_swap_combined_bytes": MEM_APP},
            "resources_client": {"cpu_limit": 0.5, "memory_limit_bytes": MEM_CLIENT,
                                 "memory_swap_combined_bytes": MEM_CLIENT}}


def topology(network, names):
    net = json.loads(checked("docker", "network", "inspect", network))[0]
    if net.get("Driver") != "bridge" or net.get("Internal") is not True:
        raise ValueError("rede nao e bridge interna")
    containers = {}
    for role, name in names.items():
        obj = json.loads(checked("docker", "inspect", name))[0]
        config = obj.get("HostConfig") or {}
        limit = MEM_CLIENT if role == "client" else MEM_APP
        if (obj.get("Image") != IMAGE_ID
                or not obj.get("State", {}).get("Running")
                or obj.get("RestartCount") != 0
                or network not in (obj.get("NetworkSettings", {}).get("Networks") or {})
                or (config.get("PortBindings") or {})
                or config.get("NanoCpus") != 500000000
                or config.get("Memory") != limit
                or config.get("MemorySwap") != limit):
            raise ValueError(f"topologia/limites divergentes no container {name}")
        containers[role] = {
            "id": obj["Id"], "name": name, "image_id": obj["Image"],
            "restart_count": obj.get("RestartCount"),
            "nano_cpus": config.get("NanoCpus"),
            "memory_bytes": config.get("Memory"),
            "memory_swap_bytes": config.get("MemorySwap"),
            "ip": (obj.get("NetworkSettings", {}).get("Networks") or {}).get(network, {}).get("IPAddress"),
        }
    if len({x["id"] for x in containers.values()}) != len(containers):
        raise ValueError("identidades Docker repetidas")
    return {"network": network, "containers": containers, "internal": True}


def http(name, path, payload=None):
    argv = ["docker", "exec", name, "python", "-c", HTTP_CLIENT, path]
    if payload is not None:
        argv.append(json.dumps(payload, separators=(",", ":"), ensure_ascii=True))
    return json.loads(checked(*argv, timeout=30))


def logs(names):
    return {role: [json.loads(line) for line in checked("docker", "logs", names[role]).splitlines()
                   if line.strip()] for role in ROLES}


def states(names):
    return {role: http(names[role], "/state") for role in ROLES}


def cold_check(names):
    initial = states(names)
    for role in ROLES:
        s = initial[role]
        if s.get("ready") is not False or s.get("run_id") is not None:
            raise ValueError(f"{role} nao esta frio")
        if any(item.get("event_type") == "mutation" for item in logs(names)[role]):
            raise ValueError(f"{role} ja sofreu mutacao")
    if initial["attribute-source"].get("attributes") != {"atA": 0, "atB": 0}:
        raise ValueError("estado de atributo nao inicial")
    return initial


def cgroup_sample(names):
    values = []
    for role, name in names.items():
        proc = command("docker", "exec", name, "python", "-c", RESOURCE_SCRIPT, timeout=20)
        if proc.returncode:
            raise RuntimeError(f"cgroup ilegivel em {role}: {proc.stderr[-200:]}")
        data = json.loads(proc.stdout)
        values.append({"role": role, "container": name,
                       "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                       **data})
    return values


class Sampler:
    def __init__(self, names, period):
        self.names, self.period = names, period
        self.samples, self.errors = [], []
        self.done = threading.Event()
        self.worker = threading.Thread(target=self.collect, daemon=True)

    def once(self):
        self.samples.extend(cgroup_sample(self.names))

    def collect(self):
        while not self.done.is_set():
            try:
                self.once()
            except Exception as exc:
                self.errors.append(f"{type(exc).__name__}: {exc}")
            self.done.wait(self.period)

    def start(self):
        try:
            self.once()
        except Exception as exc:
            self.errors.append(f"baseline: {exc}")
        self.worker.start()

    def stop(self):
        self.done.set()
        self.worker.join(timeout=35)
        if self.worker.is_alive():
            self.errors.append("sampler nao finalizou")
        try:
            self.once()
        except Exception as exc:
            self.errors.append(f"after: {exc}")


def validate_transport(inputs, all_logs, final, before, after):
    source, logic, executor = (all_logs[r] for r in ROLES)
    attr_out = [x["payload"] for x in source if x.get("event_type") == "send"
                and x.get("path") == "/notifications/attribute"]
    attr_in = [x["payload"] for x in logic if x.get("event_type") == "mutation"
               and x.get("path") == "/notifications/attribute" and x.get("status") == 200]
    cond_out = [x["payload"] for x in logic if x.get("event_type") == "send"
                and x.get("path") == "/notifications/condition"]
    cond_in = [x["payload"] for x in executor if x.get("event_type") == "mutation"
               and x.get("path") == "/notifications/condition" and x.get("status") == 200]
    counts = characterize(inputs)
    return {
        "attribute_causality": attr_out == attr_in and len(attr_out) == counts["changed"],
        "condition_causality": cond_out == cond_in and len(cond_out) == counts["condition_transitions"],
        "effects_logged": [x["payload"] for x in executor if x.get("event_type") == "effect"]
                          == final["rule-executor"]["effects"],
        "container_identities_stable": before["containers"] == after["containers"],
    }


def run(args, rows, network, names):
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    report = {"scenario": "C2", "run_id": args.run_id, "status": "FAIL",
              "phase": "preflight", "started_snapshot": False,
              "started_changes": False, "network": network}
    created = False
    try:
        setup = preflight(network, names)
        write_json(output / "manifest.json", {
            **setup, "scenario": "C2", "run_id": args.run_id, "fixture": str(args.fixture),
            "fixture_sha256": hash_file(args.fixture), "seed": rows[0]["seed"],
            "requests": len(rows), "client": "docker exec -i python - inside client container",
            "cpu_sampler_note": "INTRUSIVE: docker exec cria processos amostradores; apenas diagnostico",
            "memory_sampler_note": "memory.current e memory.peak incluem atividade amostradora; nao comparar como workingSetBytes",
            "batch_timeout_s": args.batch_timeout, "period_s": args.period})
        rebased = rebase(rows, args.run_id)
        write_jsonl(output / "inputs.jsonl", rebased)
        write_jsonl(output / "expected.jsonl", calculate_expected_effects(rebased))
        report["phase"] = "creation"
        checked("docker", "network", "create", "--driver", "bridge",
                "--internal", "--label", "tcc2.e11=pilot", network)
        created = True
        # Executar dependencias antes da fonte; nenhuma porta publicada.
        for role in ("rule-executor", "logic-engine", "attribute-source"):
            checked(*build_service_command(role, names[role], network))
        checked(*build_client_command(names["client"], network))
        # Readiness GET sem alterar estado; logs e IDs ainda serao auditados.
        for attempt in range(20):
            try:
                current = topology(network, names)
                if all(http(names[r], "/health/live").get("live") is True for r in ROLES):
                    break
            except (RuntimeError, ValueError, KeyError):
                pass
            time.sleep(0.5)
        else:
            raise ValueError("readiness nao confirmado")
        before = topology(network, names)
        write_json(output / "topology-start.json", before)
        cold = cold_check(names)
        write_json(output / "states-cold.json", cold)
        report["phase"] = "snapshot"
        report["started_snapshot"] = True
        snapshot = http(names["attribute-source"], "/init/snapshot", {"run_id": args.run_id})
        write_json(output / "snapshot-response.json", snapshot)
        if snapshot.get("ready") is not True or snapshot.get("duplicate") is not False:
            raise ValueError("snapshot nao aprovado; NAO repetir")
        first = states(names)
        write_json(output / "states-after-snapshot.json", first)
        if not all(x.get("run_id") == args.run_id and x.get("ready") is True
                   for x in first.values()) or first["rule-executor"].get("effects"):
            raise ValueError("snapshot nao propagado aos tres servicos")
        sampler = Sampler(names, args.period)
        report["phase"] = "batch"
        sampler.start()
        try:
            report["started_changes"] = True
            try:
                batch = command("docker", "exec", "-i", names["client"], "python", "-",
                                "--url", "http://attribute-source:8080",
                                "--timeout", str(args.timeout),
                                stdin=client_program(rebased), timeout=args.batch_timeout)
            except subprocess.TimeoutExpired as exc:
                for file, content in (
                    ("client.stdout.partial.log", exc.stdout),
                    ("client.stderr.partial.log", exc.stderr)):
                    if isinstance(content, bytes):
                        content = content.decode("utf-8", errors="replace")
                    (output / file).write_text(content or "", encoding="utf-8")
                raise RuntimeError("timeout: POST remoto incerto; NAO repetir") from exc
            (output / "client.stdout.jsonl").write_text(batch.stdout, encoding="utf-8")
            (output / "client.stderr.log").write_text(batch.stderr, encoding="utf-8")
        finally:
            sampler.stop()
            write_jsonl(output / "metrics-cgroup-intrusive.jsonl", sampler.samples)
            write_json(output / "metrics-errors.json", sampler.errors)
            write_csv(output / "metrics-cgroup-intrusive.csv", sampler.samples,
                      ("role", "container", "retrieved_utc", "capture_utc",
                       "cpu_usage_usec", "cpu_nr_throttled", "cpu_throttled_usec",
                       "memory_current_bytes", "memory_peak_lifetime_bytes"))
        records = [json.loads(x) for x in batch.stdout.splitlines() if x.strip()]
        if batch.returncode != 0 or not records or records[-1].get("status") != "PASS":
            raise ValueError("lote com falha, nao repetir")
        write_json(output / "batch-summary.json", records[-1])
        write_csv(output / "requests.csv", [
            {"step": x.get("step"), "status": x.get("status"),
             "duration_ns": x.get("duration_ns"),
             "changed": (x.get("response") or {}).get("changed")}
            for x in records[:-1]], ("step", "status", "duration_ns", "changed"))
        after = topology(network, names)
        write_json(output / "topology-end.json", after)
        final = states(names)
        write_json(output / "states-final.json", final)
        write_jsonl(output / "effects.jsonl", final["rule-executor"]["effects"])
        all_logs = logs(names)
        for role in ROLES:
            write_jsonl(output / f"{role}-logs.jsonl", all_logs[role])
        validated = check_run(rebased, records, final)
        validated["transport"] = validate_transport(rebased, all_logs, final, before, after)
        validated["metric_quality"] = {
            "available": bool(sampler.samples), "measurement_approved": False,
            "reason": "docker exec intrusivo e fronteiras temporais nao calibradas",
            "errors": sampler.errors,
            "samples": len(sampler.samples)}
        validated["status"] = ("PASS" if validated["status"] == "PASS"
                               and all(validated["transport"].values()) else "FAIL")
        report["status"] = validated["status"]
        report["validation"] = validated
        report["phase"] = "complete"
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        if created:
            for action, fn in (
                ("topology", lambda: topology(network, names)),
                ("states", lambda: states(names)),
                ("logs", lambda: logs(names))):
                try:
                    data = fn()
                    if action == "logs":
                        for role in ROLES:
                            write_jsonl(output / f"{role}-recovery-logs.jsonl", data[role])
                    else:
                        write_json(output / f"{action}-recovery.json", data)
                except Exception as recovery_exc:
                    report[f"{action}_recovery_error"] = str(recovery_exc)
    finally:
        write_json(output / "validation.json", report)
        artifact = archive(output)
        print("STATUS:", report["status"])
        print("ETAPA:", report["phase"])
        print("ZIP:", artifact["zip"])
        print("ZIP_SHA256:", artifact["sha256"])
        print("CONTAINERS PRESERVADOS:", ", ".join(names.values()))
        if report["status"] != "PASS":
            print("FALHA: preservados rede/containers. NAO REPETIR snapshot ou lote.")
    return report["status"] == "PASS"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--batch-timeout", type=int, default=600)
    parser.add_argument("--period", type=float, default=1.0)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.timeout <= 120 or not 10 <= args.batch_timeout <= 3600 or not 0.5 <= args.period <= 20:
        parser.error("time-outs ou periodo invalidos")
    rows = read_jsonl(args.fixture)
    network, names = validate_fixture(args.label, args.run_id, rows)
    if not args.execute:
        print(json.dumps({
            "status": "PLAN_ONLY", "scenario": "C2", "network": network,
            "containers": names, "run_id": args.run_id, "size": len(rows),
            "expected": characterize(rebase(rows, args.run_id)),
            "execute": False}, indent=2, ensure_ascii=False))
        return 0
    return 0 if run(args, rows, network, names) else 2


if __name__ == "__main__":
    sys.exit(main())
