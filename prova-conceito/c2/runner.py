"""E08-D11: executa fixture no C2 ja inicializado; preserva evidencias sem reiniciar containers."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from c0.io import read_jsonl, validate_input, write_jsonl
from c0.runner import PROJECT_ROOT, compare_effects, git_sha, sha256_file, write_json

IMAGE_TAG = "tcc2-pon:c2-e08-dbefcd2cf3d2"
BUILD_SHA = "dbefcd2cf3d2fbf220cff8eda34d52189e08192a"
NETWORK = "tcc2-pon-c2"
CONTAINERS = {
    "attribute-source": "tcc2-c2-attribute-source",
    "logic-engine": "tcc2-c2-logic-engine",
    "rule-executor": "tcc2-c2-rule-executor",
}
# subprocess com lista de argumentos evita reinterpretação das aspas no PowerShell.
HTTP_CLIENT = '''import json,sys,urllib.request
path=sys.argv[1]
payload=json.loads(sys.argv[2]) if len(sys.argv)>2 else None
body=None if payload is None else json.dumps(payload,allow_nan=False).encode("utf-8")
req=urllib.request.Request("http://127.0.0.1:8080"+path,data=body,headers={"Content-Type":"application/json"})
with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=10) as res:
    print(json.dumps(json.load(res),ensure_ascii=True,sort_keys=True))
'''


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def command(*args):
    completed = subprocess.run(
        [str(a) for a in args], cwd=PROJECT_ROOT, capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"comando falhou ({completed.returncode}): {args[:4]}\n"
            f"stdout: {completed.stdout[-1500:]}\nstderr: {completed.stderr[-1500:]}"
        )
    return completed.stdout


def http(role, path, payload=None):
    args = ["docker", "exec", CONTAINERS[role], "python", "-c", HTTP_CLIENT, path]
    if payload is not None:
        args.append(json.dumps(payload, ensure_ascii=True, separators=(",", ":")))
    return json.loads(command(*args))


def check_snapshot_state(states, run_id):
    """Exige snapshot pronto sem nenhum passo ja aplicado."""
    for role, state in states.items():
        if not (state["ready"] is True and state["run_id"] == run_id
                and state["snapshot_version"] == f"{run_id}:snapshot:0"):
            raise ValueError(f"snapshot inicial divergente: {role}")
    for role in ("attribute-source", "logic-engine"):
        state = states[role]
        if (state["attributes"] != {"atA": 0, "atB": 0}
                or state["sequences"] != {"atA": 0, "atB": 0}):
            raise ValueError(f"estado inicial divergente: {role}")
    source = states["attribute-source"]
    logic = states["logic-engine"]
    executor = states["rule-executor"]
    if source["pending_request_id"] is not None:
        raise ValueError("produtor com envio pendente")
    if (logic["condition"] is not False or logic["condition_sequence"] != 0
            or logic["received_ids"] or logic["condition_events"] or logic["faulted"]):
        raise ValueError("avaliador nao esta no snapshot inicial")
    if (executor["approved"] is not False or executor["condition_sequence"] != 0
            or executor["effects"] or executor["received_ids"] or executor["faulted"]):
        raise ValueError("executor nao esta no snapshot inicial")


def read_service_logs():
    logs = {}
    for role, name in CONTAINERS.items():
        raw = command("docker", "logs", name)
        logs[role] = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return logs


def inspect_topology():
    net = json.loads(command("docker", "network", "inspect", NETWORK))[0]
    if net["Driver"] != "bridge" or net["Internal"] is not True:
        raise ValueError("rede nao e bridge interna")
    image = json.loads(command("docker", "image", "inspect", IMAGE_TAG))[0]
    if (image["Os"] != "linux" or image["Architecture"] != "amd64"
            or image["Config"]["Labels"].get("org.opencontainers.image.revision") != BUILD_SHA):
        raise ValueError("imagem divergente do build aprovado")
    containers = {}
    for role, name in CONTAINERS.items():
        info = json.loads(command("docker", "inspect", name))[0]
        if (info["State"]["Running"] is not True
                or NETWORK not in info["NetworkSettings"]["Networks"]
                or info["Image"] != image["Id"]
                or info["HostConfig"]["PortBindings"]):
            raise ValueError(f"topologia inesperada: {name}")
        containers[role] = {"name": name, "id": info["Id"], "image_id": info["Image"]}
    if len({item["id"] for item in containers.values()}) != 3:
        raise ValueError("IDs Docker repetidos")
    return {"network": NETWORK, "internal": True, "image_tag": IMAGE_TAG,
            "image_id": image["Id"], "image_revision": BUILD_SHA,
            "containers": containers}


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    fixture = PROJECT_ROOT / "fixtures" / "c0_minimo.jsonl"
    expected_file = PROJECT_ROOT / "fixtures" / "c0_esperado.jsonl"
    rows = read_jsonl(fixture)
    run_id, seed = validate_input(rows)
    expected = read_jsonl(expected_file)
    c0, execution, oracle = compare_effects(rows, expected)
    report = {"scenario": "C2", "run_id": run_id, "status": "FAIL", "checks": {}}
    manifest = {"scenario": "C2", "run_id": run_id, "seed": seed,
                "timestamp_utc": utc_now(), "git_sha": git_sha(),
                "python_host": platform.python_version(),
                "host_platform": platform.platform(),
                "fixture_sha256": sha256_file(fixture),
                "expected_sha256": sha256_file(expected_file),
                "note": "tres conteineres mesmo host; sem Kubernetes nem benchmark"}
    transcript = []
    started_changes = False
    try:
        if c0["status"] != "PASS" or oracle != expected:
            raise ValueError("C0 ou oraculo independente divergentes ANTES do envio")
        if command("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
            raise ValueError("branch incorreta")
        if command("git", "status", "--porcelain").strip():
            raise ValueError("alteracoes locais detectadas")
        delta = subprocess.run(
            ["git", "diff", "--quiet", BUILD_SHA, "HEAD", "--",
             "pon", "c1", "Dockerfile", ".dockerignore"],
            cwd=PROJECT_ROOT, check=False,
        )
        if delta.returncode:
            raise ValueError("codigo runtime mudou desde build aprovado")
        manifest.update(inspect_topology())
        initial = {role: http(role, "/state") for role in CONTAINERS}
        write_json(output / "states-initial.json", initial)
        check_snapshot_state(initial, run_id)
        # Detecta inclusive passo 1 redundante, que nao alteraria o /state.
        for item in read_service_logs()["attribute-source"]:
            if (item.get("event_type") == "mutation"
                    and item.get("path") == "/attributes/change"):
                raise ValueError("passos anteriores nos logs: NAO repetir a fixture")

        shutil.copyfile(fixture, output / "fixture.jsonl")
        shutil.copyfile(expected_file, output / "expected.jsonl")
        write_jsonl(output / "c0-effects.jsonl", execution["effects"])
        write_jsonl(output / "oracle_independente.jsonl", oracle)
        write_json(output / "manifest.json", manifest)
        values, sequences = {"atA": 0, "atB": 0}, {"atA": 0, "atB": 0}
        for row in rows:
            payload = {key: value for key, value in row.items() if key != "seed"}
            started_changes = True
            response = http("attribute-source", "/attributes/change", payload)
            name = row["entity_id"]
            changed = values[name] != row["value"]
            if changed:
                values[name] = row["value"]
                sequences[name] += 1
            event_id = f"{run_id}:{name}:{sequences[name]}" if changed else None
            transcript.append({"timestamp_utc": utc_now(), "step": row["step"],
                               "payload": payload, "response": response})
            write_jsonl(output / "http.jsonl", transcript)
            if not (response["changed"] is changed
                    and response["sequence"] == sequences[name]
                    and response["event_id"] == event_id
                    and response["duplicate_request"] is False):
                raise ValueError(f"resposta inesperada no passo {row['step']}: {response}")

        final = {role: http(role, "/state") for role in CONTAINERS}
        write_json(output / "states-final.json", final)
        source = final["attribute-source"]
        logic = final["logic-engine"]
        executor = final["rule-executor"]
        effects = executor["effects"]
        write_jsonl(output / "effects.jsonl", effects)
        logs = read_service_logs()
        attr_sends = [r["payload"] for r in logs["attribute-source"]
                      if r.get("event_type") == "send" and r.get("path") == "/notifications/attribute"]
        attr_received = [r["payload"] for r in logs["logic-engine"]
                         if r.get("event_type") == "mutation"
                         and r.get("path") == "/notifications/attribute" and r.get("status") == 200]
        cond_sends = [r["payload"] for r in logs["logic-engine"]
                      if r.get("event_type") == "send" and r.get("path") == "/notifications/condition"]
        cond_received = [r["payload"] for r in logs["rule-executor"]
                         if r.get("event_type") == "mutation"
                         and r.get("path") == "/notifications/condition" and r.get("status") == 200]
        effect_logs = [r["payload"] for r in logs["rule-executor"]
                       if r.get("event_type") == "effect"]
        checks = {
            "transport_and_causality": (
                len(attr_sends) == 5 and attr_sends == attr_received
                and [r["event_id"] for r in attr_sends] == logic["received_ids"]
                and len(cond_sends) == 3
                and cond_sends == cond_received == logic["condition_events"]
                and [r["event_id"] for r in cond_sends] == executor["received_ids"]
                and effect_logs == effects
            ),
            "matches_manual": effects == expected,
            "matches_oracle": effects == oracle,
            "matches_c0": effects == execution["effects"],
            "effect_steps": [e["step"] for e in effects] == [3, 7],
            "final_attributes": source["attributes"] == logic["attributes"] == {"atA": 6, "atB": 1},
            "attribute_sequences": source["sequences"] == logic["sequences"] == {"atA": 2, "atB": 3},
            "condition": logic["condition"] is True and executor["approved"] is True,
            "condition_sequence": logic["condition_sequence"] == executor["condition_sequence"] == 3,
            "event_counts": len(logic["received_ids"]) == 5 and len(executor["received_ids"]) == 3,
            "ready_no_fault": all(s["ready"] is True for s in final.values())
                              and logic["faulted"] is False and executor["faulted"] is False,
        }
        report["checks"] = checks
        report["status"] = "PASS" if all(checks.values()) else "FAIL"
        if report["status"] != "PASS":
            raise ValueError("divergencia nas verificacoes C2")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, AssertionError) as error:
        report["error"] = str(error)
        report["status"] = "FAIL"
    finally:
        report["started_changes"] = started_changes
        for role, name in CONTAINERS.items():
            try:
                (output / f"{role}.jsonl").write_text(
                    command("docker", "logs", name), encoding="utf-8")
            except (RuntimeError, OSError) as error:
                (output / f"{role}.capture-error.txt").write_text(
                    str(error), encoding="utf-8")
        if not (output / "manifest.json").exists():
            write_json(output / "manifest.json", manifest)
        write_json(output / "validation.json", report)
        (output / "checksums.sha256").write_text("".join(
            f"{sha256_file(path)}  {path.name}\n"
            for path in sorted(output.iterdir()) if path.name != "checksums.sha256"
        ), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = run(args.output)
    except (OSError, ValueError) as error:
        print(f"E08-D11: FALHA ANTES DA RODADA: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Evidencias: {args.output.resolve()}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
