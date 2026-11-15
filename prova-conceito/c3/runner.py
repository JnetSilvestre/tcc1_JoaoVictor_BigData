"""E09-I04: rodada C3 UNICA, sem snapshot/restart, com provas e checksums.

Uso (na pasta prova-conceito):
    python -m c3.runner --output resultados-locais/c3-e09-i04-v1

A execucao e mutante e NAO deve ser repetida. Em falha, preservar o ZIP
e investigar os estados e logs antes de tentar qualquer nova rodada.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

from c0.io import read_jsonl, validate_input, write_jsonl
from c0.oracle import calculate_expected_effects
from c0.runner import compare_effects, git_sha, sha256_file, write_json

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = "kind-tcc2-pon"
NS = "tcc2-pon"
RUN_ID = "c3-e09-i03-v1"  # snapshot JA executado e comprovado em E09-I03
SCENARIO = "C3"
EXECUTION_LABEL = "E09-I04"
ROLES = ("attribute-source", "logic-engine", "rule-executor")
IMAGE = "tcc2-pon:c2-e08-dbefcd2cf3d2"
IMAGE_ID = "sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a"
BUILD_SHA = "dbefcd2cf3d2fbf220cff8eda34d52189e08192a"

# Script executado apenas dentro do Pod source; todas as requisicoes HTTP
# chegam via DNS do SERVICE de destino, nao via porta publicada no host.
HTTP_BODY = """
host, path, payload = params["host"], params["path"], params["payload"]
body = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
req = urllib.request.Request(
    "http://" + host + ":8080" + path,
    data=body, headers={"Content-Type": "application/json"},
)
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
    with opener.open(req, timeout=10) as response:
        print(json.dumps({"status": response.status, "body": json.load(response)},
                         sort_keys=True))
except urllib.error.HTTPError as error:
    with error:
        print(json.dumps({"status": error.code, "body": json.load(error)},
                         sort_keys=True))
"""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def command(*args, stdin=None):
    try:
        proc = subprocess.run(
            [str(x) for x in args], input=stdin, cwd=ROOT, text=True,
            encoding="utf-8", errors="replace", capture_output=True,
            check=False, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"falha/timeout no comando {args[:5]}: {exc}") from exc
    if proc.returncode != 0:
        raise RuntimeError(
            f"comando {args[:6]} exit={proc.returncode}\n"
            f"stdout: {proc.stdout[-1200:]}\nstderr: {proc.stderr[-1200:]}"
        )
    return proc.stdout


def kube(*args, stdin=None):
    return command("kubectl", "--context", CONTEXT, "-n", NS, *args, stdin=stdin)


def kubedata(*args):
    return json.loads(kube(*args))


def http(source_pod, role, path, payload=None):
    params = json.dumps(
        {"host": role, "path": path, "payload": payload}, ensure_ascii=True,
        separators=(",", ":"),
    )
    encoded = base64.b64encode(params.encode("ascii")).decode("ascii")
    script = (
        "import base64,json,urllib.request,urllib.error\n"
        f"params=json.loads(base64.b64decode('{encoded}'))\n"
        + HTTP_BODY
    )
    reply = kube("exec", "-i", source_pod, "--", "python", "-", stdin=script)
    result = json.loads(reply.strip())
    if not isinstance(result, dict) or set(result) != {"status", "body"}:
        raise ValueError(f"resposta inesperada {role}{path}: {result}")
    return result["status"], result["body"]


def append_jsonl(path, value):
    with Path(path).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_logs(pod):
    text = kube("logs", f"pod/{pod}")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def topology():
    pods_raw = kubedata("get", "pods", "-o", "json")
    deployments = kubedata("get", "deployments", "-o", "json")
    services = kubedata("get", "services", "-o", "json")
    nodes = json.loads(command("kubectl", "--context", CONTEXT, "get", "nodes", "-o", "json"))
    pods = {}
    for item in pods_raw["items"]:
        role = item["metadata"].get("labels", {}).get("app")
        if role in ROLES:
            if role in pods:
                raise ValueError(f"mais de um Pod para {role}")
            pods[role] = item
    if set(pods) != set(ROLES):
        raise ValueError(f"Pods incompletos: {list(pods)}")
    deploys = {d["metadata"]["name"]: d for d in deployments["items"]}
    svcs = {s["metadata"]["name"]: s for s in services["items"]}
    for role in ROLES:
        pod = pods[role]
        statuses = pod.get("status", {}).get("containerStatuses") or []
        if (pod["status"]["phase"] != "Running" or len(statuses) != 1
                or statuses[0]["restartCount"] != 0
                or statuses[0]["ready"] is not True
                or pod["spec"]["containers"][0]["image"] != IMAGE):
            raise ValueError(f"Pod instavel, reiniciado ou imagem divergente: {role}")
        dep = deploys[role]
        if (dep["spec"]["replicas"] != 1
                or dep.get("status", {}).get("availableReplicas") != 1
                or dep["spec"]["template"]["spec"]["containers"][0]["image"] != IMAGE):
            raise ValueError(f"Deployment inesperado: {role}")
        svc = svcs[role]
        if (svc["spec"].get("type") != "ClusterIP"
                or svc["spec"]["ports"][0]["port"] != 8080
                or svc["spec"]["selector"].get("app") != role):
            raise ValueError(f"Service inesperado: {role}")
    return {
        "pods": {r: {
            "name": pods[r]["metadata"]["name"],
            "uid": pods[r]["metadata"]["uid"],
            "node": pods[r]["spec"].get("nodeName"),
            "pod_ip": pods[r]["status"].get("podIP"),
            "container_id": pods[r]["status"]["containerStatuses"][0].get("containerID"),
            "image_id_runtime": pods[r]["status"]["containerStatuses"][0].get("imageID"),
            "restart_count": pods[r]["status"]["containerStatuses"][0]["restartCount"],
        } for r in ROLES},
        "services": {r: svcs[r]["spec"].get("clusterIP") for r in ROLES},
        "nodes": [{"name": n["metadata"]["name"],
                   "ready": any(c["type"] == "Ready" and c["status"] == "True"
                                for c in n["status"]["conditions"])}
                  for n in nodes["items"]],
        "pods_full": pods_raw,
        "deployments_full": deployments,
        "services_full": services,
        "nodes_full": nodes,
    }


def check_initial(states, logs):
    for role in ROLES:
        state = states[role]
        if not (state["ready"] is True and state["run_id"] == RUN_ID
                and state["snapshot_version"] == RUN_ID + ":snapshot:0"):
            raise ValueError(f"snapshot ausente/divergente em {role}")
        snapshot_mutations = [
            e for e in logs[role] if e.get("event_type") == "mutation"
            and e.get("path") == "/init/snapshot"
        ]
        if len(snapshot_mutations) != 1 or snapshot_mutations[0].get("status") != 200:
            raise ValueError(f"snapshot duplicado ou ausente nos logs de {role}")
    for role in ("attribute-source", "logic-engine"):
        if states[role]["attributes"] != {"atA": 0, "atB": 0}:
            raise ValueError(f"atributos ja alterados: {role}")
        if states[role]["sequences"] != {"atA": 0, "atB": 0}:
            raise ValueError(f"watermarks ja alterados: {role}")
    source, logic, executor = (states[r] for r in ROLES)
    if source["pending_request_id"] is not None:
        raise ValueError("requisicao pendente no produtor")
    if (logic["condition"] is not False or logic["condition_sequence"] != 0
            or logic["received_ids"] or logic["condition_events"]
            or logic["faulted"]):
        raise ValueError("logic-engine nao esta no snapshot frio")
    if (executor["approved"] is not False or executor["condition_sequence"] != 0
            or executor["received_ids"] or executor["effects"] or executor["faulted"]):
        raise ValueError("rule-executor nao esta no snapshot frio")
    for role in ROLES:
        mutations = [e for e in logs[role] if e.get("event_type") == "mutation"]
        if any(e.get("path") != "/init/snapshot" for e in mutations):
            raise ValueError(f"historico incremental detectado em {role}; NAO repetir a fixture")
    return True


def rebase_effects(effects, old_run_id):
    rebased = []
    for effect in effects:
        converted = dict(effect)
        converted["run_id"] = RUN_ID
        for key in ("event_id", "caused_by", "attribute_event_id"):
            if not effect[key].startswith(old_run_id + ":"):
                raise ValueError(f"ID nao corresponde ao fixture aprovado: {key}")
            converted[key] = RUN_ID + effect[key][len(old_run_id):]
        rebased.append(converted)
    return rebased


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    input_file = ROOT / "fixtures" / "c0_minimo.jsonl"
    expected_file = ROOT / "fixtures" / "c0_esperado.jsonl"
    report = {"scenario": SCENARIO, "run_id": RUN_ID, "status": "FAIL",
              "started_changes": False, "checks": {}}
    manifest = {
        "scenario": SCENARIO, "run_id": RUN_ID, "timestamp_utc": utc_now(),
        "context": CONTEXT, "namespace": NS, "image_tag": IMAGE,
        "approved_image_id": IMAGE_ID, "image_revision": BUILD_SHA,
        "host_python": platform.python_version(), "host_os": platform.platform(),
        "git_sha": git_sha(), "original_input_sha256": sha256_file(input_file),
        "original_expected_sha256": sha256_file(expected_file),
        "note": f"Uma rodada funcional {SCENARIO}, tres Pods; sem benchmark nem medicao CPU/RAM",
    }
    print(f"{EXECUTION_LABEL}: preparando evidencias em", output, flush=True)
    shutil.copyfile(input_file, output / "fixture-original.jsonl")
    shutil.copyfile(expected_file, output / "expected-original.jsonl")
    source_pod = None
    try:
        if command("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
            raise ValueError("branch incorreta")
        if command("git", "status", "--porcelain").strip():
            raise ValueError("Git com alteracoes locais; interromper")
        command("git", "diff", "--quiet", BUILD_SHA, "HEAD", "--",
                "pon", "c1", "Dockerfile", ".dockerignore")
        image = json.loads(command("docker", "image", "inspect", IMAGE))[0]
        if (image["Id"] != IMAGE_ID or image["Os"] != "linux"
                or image["Architecture"] != "amd64"
                or image["Config"]["Labels"].get("org.opencontainers.image.revision") != BUILD_SHA):
            raise ValueError("imagem local nao corresponde a imagem C2 aprovada")

        originals = read_jsonl(input_file)
        old_run_id, seed = validate_input(originals)
        manual = read_jsonl(expected_file)
        c0, c0_execution, original_oracle = compare_effects(originals, manual)
        if (c0["status"] != "PASS" or manual != original_oracle
                or [e["step"] for e in manual] != [3, 7]):
            raise ValueError("oraculo/C0/manual divergentes ANTES da rodada")

        rows = [{**row, "run_id": RUN_ID} for row in originals]
        expected = rebase_effects(manual, old_run_id)
        c0_effects = rebase_effects(c0_execution["effects"], old_run_id)
        oracle = calculate_expected_effects(rows)
        if not (expected == oracle == c0_effects):
            raise ValueError("normalizacao run_id divergente")
        manifest["seed"] = seed
        write_jsonl(output / "fixture-c3.jsonl", rows)
        write_jsonl(output / "expected-c3.jsonl", expected)
        write_jsonl(output / "oracle-independente.jsonl", oracle)
        write_jsonl(output / "c0-effects.jsonl", c0_effects)

        topo_start = topology()
        write_json(output / "topology-initial.json", topo_start)
        source_pod = topo_start["pods"]["attribute-source"]["name"]
        initial = {role: http(source_pod, role, "/state")[1] for role in ROLES}
        write_json(output / "states-initial.json", initial)
        logs_initial = {role: read_logs(topo_start["pods"][role]["name"]) for role in ROLES}
        for role, logs in logs_initial.items():
            write_jsonl(output / f"{role}-logs-initial.jsonl", logs)
        check_initial(initial, logs_initial)
        manifest["pods"] = topo_start["pods"]
        manifest["services"] = topo_start["services"]
        manifest["nodes"] = topo_start["nodes"]
        write_json(output / "manifest.json", manifest)

        print(f"{EXECUTION_LABEL} PRECHECK: PASS (snapshot unico, estado inicial, imagem e oraculo)", flush=True)
        values = {"atA": 0, "atB": 0}
        sequences = {"atA": 0, "atB": 0}
        for row in rows:
            payload = {key: value for key, value in row.items() if key != "seed"}
            append_jsonl(output / "attempts.jsonl", {
                "timestamp_utc": utc_now(), "step": row["step"],
                "intent": "BEFORE_POST", "payload": payload,
            })
            report["started_changes"] = True
            status, response = http(source_pod, "attribute-source", "/attributes/change", payload)
            append_jsonl(output / "http.jsonl", {
                "timestamp_utc": utc_now(), "step": row["step"],
                "http_status": status, "payload": payload, "response": response,
            })
            name = row["entity_id"]
            changed = values[name] != row["value"]
            if changed:
                values[name] = row["value"]
                sequences[name] += 1
            event_id = f"{RUN_ID}:{name}:{sequences[name]}" if changed else None
            if not (status == 200 and response["changed"] is changed
                    and response["sequence"] == sequences[name]
                    and response["event_id"] == event_id
                    and response["duplicate_request"] is False):
                raise ValueError(f"resposta HTTP inesperada no passo {row['step']}: {response}")
            print(f"PASSO {row['step']}: HTTP=200 changed={changed}", flush=True)

        final = {role: http(source_pod, role, "/state")[1] for role in ROLES}
        write_json(output / "states-final.json", final)
        topo_final = topology()
        write_json(output / "topology-final.json", topo_final)
        if topo_start["pods"] != topo_final["pods"]:
            raise ValueError("identidade/restart/node do Pod mudou durante a rodada")

        logs_final = {role: read_logs(topo_final["pods"][role]["name"]) for role in ROLES}
        for role, logs in logs_final.items():
            write_jsonl(output / f"{role}-logs-final.jsonl", logs)

        source, logic, executor = (final[r] for r in ROLES)
        effects = executor["effects"]
        write_jsonl(output / "effects.jsonl", effects)

        attr_sends = [e["payload"] for e in logs_final["attribute-source"]
                      if e.get("event_type") == "send"
                      and e.get("path") == "/notifications/attribute"]
        attr_received = [e["payload"] for e in logs_final["logic-engine"]
                         if e.get("event_type") == "mutation"
                         and e.get("path") == "/notifications/attribute"
                         and e.get("status") == 200]
        cond_sends = [e["payload"] for e in logs_final["logic-engine"]
                      if e.get("event_type") == "send"
                      and e.get("path") == "/notifications/condition"]
        cond_received = [e["payload"] for e in logs_final["rule-executor"]
                         if e.get("event_type") == "mutation"
                         and e.get("path") == "/notifications/condition"
                         and e.get("status") == 200]
        effect_logs = [e["payload"] for e in logs_final["rule-executor"]
                       if e.get("event_type") == "effect"]
        source_changes = [e for e in logs_final["attribute-source"]
                          if e.get("event_type") == "mutation"
                          and e.get("path") == "/attributes/change"
                          and e.get("status") == 200]
        checks = {
            "seven_steps": len(source_changes) == 7,
            "transport_and_causality": (
                len(attr_sends) == 5 and attr_sends == attr_received
                and [e["event_id"] for e in attr_sends] == logic["received_ids"]
                and len(cond_sends) == 3
                and cond_sends == cond_received == logic["condition_events"]
                and [e["event_id"] for e in cond_sends] == executor["received_ids"]
                and effect_logs == effects
            ),
            "matches_manual": effects == expected,
            "matches_independent_oracle": effects == oracle,
            "matches_c0": effects == c0_effects,
            "steps_3_7": [e["step"] for e in effects] == [3, 7],
            "final_attributes": source["attributes"] == logic["attributes"] == {"atA": 6, "atB": 1},
            "attribute_sequences": source["sequences"] == logic["sequences"] == {"atA": 2, "atB": 3},
            "condition_and_executor": logic["condition"] is True and executor["approved"] is True,
            "condition_sequence": logic["condition_sequence"] == executor["condition_sequence"] == 3,
            "received_counts": len(logic["received_ids"]) == 5 and len(executor["received_ids"]) == 3,
            "ready_and_no_fault": all(s["ready"] is True for s in final.values())
                                  and logic["faulted"] is False and executor["faulted"] is False,
            "no_pending_request": source["pending_request_id"] is None,
            "same_pods": topo_start["pods"] == topo_final["pods"],
        }
        report["checks"] = checks
        if not all(checks.values()):
            raise ValueError("verificacoes C3 divergentes (ver validation.json)")
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAIL"
        report["error"] = f"{type(error).__name__}: {error}"
    finally:
        # Captura, inclusive apos falhas parciais. Nunca repete POST nem snapshot.
        if source_pod:
            for role in ROLES:
                try:
                    status, state = http(source_pod, role, "/state")
                    write_json(output / f"{role}-recovery-state.json", {
                        "status": status, "state": state,
                    })
                except Exception as error:
                    (output / f"{role}-recovery-error.txt").write_text(
                        str(error) + "\n", encoding="utf-8",
                    )
            for role in ROLES:
                try:
                    pods = topology()["pods"]
                    records = read_logs(pods[role]["name"])
                    write_jsonl(output / f"{role}-logs-captured.jsonl", records)
                except Exception as error:
                    (output / f"{role}-logs-error.txt").write_text(
                        str(error) + "\n", encoding="utf-8",
                    )
        if not (output / "manifest.json").exists():
            write_json(output / "manifest.json", manifest)
        write_json(output / "validation.json", report)
        (output / "checksums.sha256").write_text(
            "".join(f"{sha256_file(item)}  {item.name}\n"
                    for item in sorted(output.iterdir())
                    if item.is_file() and item.name != "checksums.sha256"),
            encoding="utf-8",
        )
        zip_path = output.with_suffix(".zip")
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
            for item in sorted(output.iterdir()):
                if item.is_file():
                    archive.write(item, arcname=item.name)
        print(f"{EXECUTION_LABEL}:", report["status"], flush=True)
        if report["status"] != "PASS":
            print("ERRO:", report.get("error"), flush=True)
            print("POST iniciado:", report["started_changes"], flush=True)
            print("Nao repetir a rodada; preservar as evidencias.", flush=True)
        else:
            print("Checks aprovados:", len(report["checks"]), "/", len(report["checks"]),
                  flush=True)
            print("Efeitos esperados/observados:", 2, "/", 2, flush=True)
        print("ZIP:", zip_path.resolve(), flush=True)
        print("ZIP_BYTES:", zip_path.stat().st_size, flush=True)
        print("ZIP_SHA256:", sha256_file(zip_path), flush=True)
    return report["status"] == "PASS"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        return 0 if run(args.output) else 1
    except (OSError, ValueError) as error:
        print(f"{EXECUTION_LABEL} BLOQUEADO antes da rodada: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
