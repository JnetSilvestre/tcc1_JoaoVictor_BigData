"""E08-D18F/G/H: três rejeições V06 em uma rodada C2, sem retries.

A bancada V06 deve estar exatamente no snapshot auditado E08-D18D.
Uma divergência aborta o próximo POST; em dúvida, NÃO repetir a rodada.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import zipfile

from c0.runner import sha256_file, write_json
from c1.protocol import (
    utc_now, validate_attribute_event, validate_condition_event,
)
from c2.v03_cold import GET, POST, call

ROLES = ("attribute-source", "logic-engine", "rule-executor")
CONTAINERS = {role: f"tcc2-v06-{role}" for role in ROLES}
NETWORK = "tcc2-pon-c2-v06"
IMAGE = "tcc2-pon:c2-e08-dbefcd2cf3d2"
REVISION = "dbefcd2cf3d2fbf220cff8eda34d52189e08192a"
RUN_ID = "v06-order-v1"
PREVIOUS_FILES = 12
EXPECTED_ERROR_GAP = "evento atrasado ou lacuna de sequence"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_logs(text):
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def read_states():
    result = {}
    for role, name in CONTAINERS.items():
        answer = json.loads(call("docker", "exec", name, "python", "-c", GET, "/state"))
        if answer != {"status": 200, "body": answer.get("body")}:
            raise ValueError("GET /state falhou: " + role)
        result[role] = answer["body"]
    return result


def read_logs():
    return {role: call("docker", "logs", name) for role, name in CONTAINERS.items()}


def verify_hash_manifest(folder, expected_count):
    manifest = folder / "checksums.sha256"
    if not manifest.is_file():
        raise ValueError("checksums.sha256 ausente")
    entries = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, separator, filename = line.partition("  ")
        filename = filename.strip()
        if (not separator or len(digest) != 64 or not filename
                or filename in entries or "/" in filename or "\\" in filename):
            raise ValueError("entrada de hash invalida")
        entries[filename] = digest.lower()
    actual = {p.name for p in folder.iterdir() if p.is_file() and p.name != manifest.name}
    if len(entries) != expected_count or set(entries) != actual:
        raise ValueError("inventario de evidencias anterior divergente")
    for name, digest in entries.items():
        if sha256_file(folder / name).lower() != digest:
            raise ValueError("hash anterior divergente: " + name)
    return entries


def topology():
    net = json.loads(call("docker", "network", "inspect", NETWORK))[0]
    if net.get("Driver") != "bridge" or net.get("Internal") is not True:
        raise ValueError("rede V06 nao e bridge internal=true")
    image = json.loads(call("docker", "image", "inspect", IMAGE))[0]
    if (image["Os"] != "linux" or image["Architecture"] != "amd64"
            or image["Config"].get("Labels", {}).get(
                "org.opencontainers.image.revision") != REVISION):
        raise ValueError("imagem Docker divergente")
    result = {"network": NETWORK, "internal": True, "image": IMAGE,
              "image_id": image["Id"], "image_revision": REVISION,
              "containers": {}}
    for role, name in CONTAINERS.items():
        info = json.loads(call("docker", "inspect", name))[0]
        if (info["State"]["Running"] is not True
                or info["State"]["Restarting"] is True
                or info["RestartCount"] != 0
                or info["Image"] != image["Id"]
                or NETWORK not in info["NetworkSettings"]["Networks"]
                or info["HostConfig"].get("PortBindings")
                or info["Config"].get("Labels", {}).get("tcc2.test") not in (None, "V06")):
            raise ValueError("conteiner V06 divergente: " + name)
        result["containers"][role] = {
            "name": name, "id": info["Id"],
            "started_at": info["State"]["StartedAt"],
            "restart_count": info["RestartCount"],
        }
    if len({v["id"] for v in result["containers"].values()}) != 3:
        raise ValueError("IDs de conteiner repetidos")
    for role in ROLES:
        v05 = json.loads(call("docker", "inspect", f"tcc2-v05-{role}"))[0]
        if v05["State"]["Running"] is not True:
            raise ValueError("V05 deixou de funcionar: " + role)
    return result


def preflight(folder):
    verify_hash_manifest(folder, PREVIOUS_FILES)
    validation = read_json(folder / "validation.json")
    if not (validation.get("status") == "PASS"
            and validation.get("criterion") == "V06"
            and validation.get("increment") == "E08-D18D"
            and validation.get("http_status") == 200
            and validation.get("ready_services") == 3
            and validation.get("initial_effects") == 0):
        raise ValueError("snapshot auditado nao aprovado")
    prior_meta = read_json(folder / "manifest.json")
    meta = topology()
    for key in ("network", "internal", "image", "image_id", "image_revision"):
        if prior_meta.get(key) != meta[key]:
            raise ValueError("metadados do snapshot divergentes: " + key)
    for role in ROLES:
        old = prior_meta["containers"][role]
        now = meta["containers"][role]
        for key in ("id", "started_at", "restart_count"):
            if key in old and old[key] != now[key]:
                raise ValueError("reinicio/substituicao V06: " + role)
    states = read_states()
    if states != read_json(folder / "states-after.json"):
        raise ValueError("estado V06 mudou desde snapshot auditado")
    for role, state in states.items():
        if (state.get("ready") is not True
                or state.get("run_id") != RUN_ID
                or state.get("snapshot_version") != RUN_ID + ":snapshot:0"
                or state.get("faulted") is True):
            raise ValueError("estado inicial V06 divergente: " + role)
    for role in ("attribute-source", "logic-engine"):
        if (states[role]["attributes"] != {"atA": 0, "atB": 0}
                or states[role]["sequences"] != {"atA": 0, "atB": 0}):
            raise ValueError("watermark V06 divergente: " + role)
    if (states["attribute-source"]["pending_request_id"] is not None
            or states["logic-engine"]["condition"] is not False
            or states["logic-engine"]["condition_sequence"] != 0
            or states["logic-engine"]["received_ids"]
            or states["logic-engine"]["condition_events"]
            or states["rule-executor"]["approved"] is not False
            or states["rule-executor"]["condition_sequence"] != 0
            or states["rule-executor"]["effects"]
            or states["rule-executor"]["received_ids"]):
        raise ValueError("V06 nao esta em estado inicial")
    logs = read_logs()
    for role in ROLES:
        previous_text = (folder / f"{role}-after.jsonl").read_text(encoding="utf-8")
        if logs[role] != previous_text:
            raise ValueError("logs V06 divergentes do snapshot: " + role)
    meta["previous_validation_sha256"] = sha256_file(folder / "validation.json")
    meta["git_sha"] = call("git", "rev-parse", "HEAD").strip()
    meta["preflight_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    return meta, states, logs


def planned_cases():
    timestamp = utc_now()
    cases = [
        ("E08-D18F", "logic-engine", "/notifications/attribute", {
            "schema_version": 1, "run_id": RUN_ID, "source": "attribute-source",
            "event_id": f"{RUN_ID}:atA:2", "entity_id": "atA",
            "sequence": 2, "value": 5, "emitted_at": timestamp, "step": 1,
            "request_id": "v06-gap-atA-2",
        }, EXPECTED_ERROR_GAP),
        ("E08-D18G", "logic-engine", "/notifications/attribute", {
            "schema_version": 1, "run_id": "v06-other-run",
            "source": "attribute-source", "event_id": "v06-other-run:atA:1",
            "entity_id": "atA", "sequence": 1, "value": 5,
            "emitted_at": timestamp, "step": 1, "request_id": "v06-other-run-1",
        }, "run_id divergente"),
        ("E08-D18H", "rule-executor", "/notifications/condition", {
            "schema_version": 1, "run_id": RUN_ID, "source": "logic-engine",
            "event_id": f"{RUN_ID}:cn1:2", "entity_id": "cn1",
            "sequence": 2, "approved": True,
            "caused_by": f"{RUN_ID}:atA:1",
            "emitted_at": timestamp, "step": 2,
        }, EXPECTED_ERROR_GAP),
    ]
    for _, role, _, payload, _ in cases:
        if role == "logic-engine":
            validate_attribute_event(payload)
        else:
            validate_condition_event(payload)
    return cases


def write_hashes(folder):
    files = sorted(p for p in folder.rglob("*") if p.is_file()
                   and p.name != "checksums.sha256")
    (folder / "checksums.sha256").write_text("".join(
        f"{sha256_file(p)}  {p.relative_to(folder).as_posix()}\n" for p in files
    ), encoding="utf-8")


def make_zip(folder):
    destination = folder.with_suffix(".zip")
    if destination.exists():
        raise ValueError("ZIP de evidencias ja existe")
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, f"{folder.name}/{path.relative_to(folder).as_posix()}")
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None or len(archive.namelist()) != len(files):
            raise ValueError("ZIP CRC/contagem incorretos")
        for path in files:
            stored = archive.read(f"{folder.name}/{path.relative_to(folder).as_posix()}")
            if stored != path.read_bytes():
                raise ValueError("ZIP com bytes divergentes")
    return destination


def execute(snapshot_folder, output):
    if call("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("branch incorreta")
    if call("git", "status", "--porcelain").strip():
        raise ValueError("Git nao esta limpo")
    if output.exists() or output.with_suffix(".zip").exists():
        raise ValueError("pasta/ZIP de saida ja existem")
    print("PREFLIGHT: verificando snapshot, topologia, hashes, logs e V05...", flush=True)
    meta, initial_states, old_logs = preflight(snapshot_folder)
    cases = planned_cases()
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "manifest.json", meta)
    write_json(output / "states-before.json", initial_states)
    for role in ROLES:
        (output / f"{role}-before.jsonl").write_text(old_logs[role], encoding="utf-8")
    result = {"scenario": "C2", "criterion": "V06", "increment": "E08-D18F-H",
              "status": "FAIL", "cases_planned": 3, "cases_completed": 0,
              "run_id": RUN_ID, "automatic_retry": False, "cases": []}
    try:
        for case_id, role, path, payload, expected_error in cases:
            case_folder = output / case_id
            case_folder.mkdir()
            if read_states() != initial_states:
                raise ValueError("estado modificado antes de " + case_id)
            if read_logs() != old_logs:
                raise ValueError("logs modificados antes de " + case_id)
            write_json(case_folder / "states-before.json", initial_states)
            write_json(case_folder / "payload.json", payload)
            write_json(case_folder / "request-intent.json", {
                "case_id": case_id, "target": CONTAINERS[role],
                "method": "POST", "path": path,
                "attempt_count": 1, "automatic_retry": False,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            })
            print(case_id + ": uma tentativa HTTP, sem retry...", flush=True)
            result["cases"].append({"case_id": case_id, "target": role,
                                    "attempted": True, "status": "FAIL"})
            # A chamada a seguir e a unica tentativa deste caso.
            reply = json.loads(call(
                "docker", "exec", CONTAINERS[role], "python", "-c", POST, path,
                json.dumps(payload, ensure_ascii=True, sort_keys=True),
                "application/json",
            ))
            write_json(case_folder / "response.json", reply)
            current_states = read_states()
            write_json(case_folder / "states-after.json", current_states)
            new_logs = read_logs()
            for r in ROLES:
                (case_folder / f"{r}-after.jsonl").write_text(new_logs[r], encoding="utf-8")
            if reply != {"status": 409, "body": {"error": expected_error}}:
                raise ValueError(case_id + ": HTTP 409/erro divergente")
            if current_states != initial_states:
                raise ValueError(case_id + ": estado funcional alterado")
            for r in ROLES:
                before_items, after_items = parse_logs(old_logs[r]), parse_logs(new_logs[r])
                extra = 1 if r == role else 0
                if (len(after_items) != len(before_items) + extra
                        or after_items[:len(before_items)] != before_items):
                    raise ValueError(case_id + ": logs alterados indevidamente: " + r)
                if extra:
                    last = after_items[-1]
                    if (last.get("event_type") != "mutation"
                            or last.get("path") != path
                            or last.get("payload") != payload
                            or last.get("status") != 409
                            or last.get("response") != {"error": expected_error}):
                        raise ValueError(case_id + ": log HTTP rejeitado divergente")
            old_logs = new_logs
            result["cases"][-1]["status"] = "PASS"
            result["cases"][-1]["observed_http"] = 409
            result["cases_completed"] += 1
            print(case_id + ": PASS, HTTP 409, estado inalterado", flush=True)
        result["status"] = "PASS"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            write_json(output / "states-after.json", read_states())
            for r, raw in read_logs().items():
                (output / f"{r}-after.jsonl").write_text(raw, encoding="utf-8")
        except Exception as exc:
            (output / "capture-error.txt").write_text(repr(exc), encoding="utf-8")
            result["status"] = "FAIL"
        result["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(output / "validation.json", result)
        write_hashes(output)
    archive = make_zip(output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("EVIDENCIAS:", output.resolve())
    print("ZIP:", archive.resolve())
    print("ZIP SHA-256:", sha256_file(archive))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = execute(args.snapshot, args.output)
    except Exception as exc:
        print("E08-D18F-H: ABORTADO NO PREFLIGHT/ARQUIVAMENTO:", exc, file=sys.stderr)
        return 2
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
