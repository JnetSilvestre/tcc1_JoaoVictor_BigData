"""TCC2 E08-D17F: replay UNICO do AttributeChanged original na bancada C2/V05.

NAO reinicializa servicos, NAO envia /attributes/change e NAO faz retry.
Aborta antes do POST se os logs/estado nao corresponderem ao primeiro evento.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

from c0.runner import PROJECT_ROOT, sha256_file, write_json
from c1.protocol import validate_attribute_event
from c2.v03_cold import GET, POST

RUN_ID = "v05-dedup-v1"
EVENT_ID = f"{RUN_ID}:atA:1"
SNAPSHOT = f"{RUN_ID}:snapshot:0"
BASE_IMAGE = "tcc2-pon:c2-e08-dbefcd2cf3d2"
BUILD_SHA = "dbefcd2cf3d2fbf220cff8eda34d52189e08192a"
NETWORK = "tcc2-pon-c2-v05"
ROLES = ("attribute-source", "logic-engine", "rule-executor")
CONTAINERS = {role: f"tcc2-v05-{role}" for role in ROLES}
EXPECTED = {
    "schema_version": 1, "event_id": EVENT_ID,
    "run_id": RUN_ID, "source": "attribute-source",
    "entity_id": "atA", "sequence": 1, "value": 5,
    "request_id": "v05-req-atA-1", "step": 1,
}


def call(*args):
    result = subprocess.run(
        [str(x) for x in args], cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        encoding="utf-8", errors="replace", timeout=30, check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"comando falhou ({result.returncode}): {args[:4]}; "
            f"stderr={result.stderr[-500:]} stdout={result.stdout[-500:]}"
        )
    return result.stdout


def json_response(role, path):
    return json.loads(call(
        "docker", "exec", CONTAINERS[role], "python", "-c", GET, path
    ))


def send_replay(original):
    # Esta e a UNICA chamada com efeito de rede do executor.
    # subprocess passa argumentos sem shell, sem alterar o JSON persistido.
    return json.loads(call(
        "docker", "exec", CONTAINERS["logic-engine"], "python", "-c", POST,
        "/notifications/attribute",
        json.dumps(original, ensure_ascii=True, sort_keys=True),
        "application/json",
    ))


def read_states():
    out = {}
    for role in ROLES:
        response = json_response(role, "/state")
        if response["status"] != 200:
            raise ValueError(f"/state inesperado: {role}: {response}")
        out[role] = response["body"]
    return out


def assert_prepared(states):
    for role, s in states.items():
        if not (s.get("service") == role
                and s.get("ready") is True
                and s.get("run_id") == RUN_ID
                and s.get("snapshot_version") == SNAPSHOT):
            raise ValueError(f"snapshot/ready inesperados: {role}")

    source, logic, executor = (states[x] for x in ROLES)
    expected_attrs = {"atA": 5, "atB": 0}
    expected_seq = {"atA": 1, "atB": 0}
    if (source.get("attributes") != expected_attrs
            or source.get("sequences") != expected_seq
            or source.get("pending_request_id") is not None):
        raise ValueError("source nao esta no estado E08-D17D")
    if (logic.get("attributes") != expected_attrs
            or logic.get("sequences") != expected_seq
            or logic.get("received_ids") != [EVENT_ID]
            or logic.get("condition") is not False
            or logic.get("condition_sequence") != 0
            or logic.get("condition_events") != []
            or logic.get("faulted") is not False):
        raise ValueError("logic-engine nao esta no estado E08-D17D")
    if (executor.get("approved") is not False
            or executor.get("condition_sequence") != 0
            or executor.get("received_ids") != []
            or executor.get("effects") != []
            or executor.get("faulted") is not False):
        raise ValueError("executor nao esta no estado E08-D17D")


def validate_original(original):
    validate_attribute_event(original)
    if set(original) != set(EXPECTED) | {"emitted_at"}:
        raise ValueError("payload possui campos inesperados")
    if any(original.get(key) != val for key, val in EXPECTED.items()):
        raise ValueError("payload nao corresponde ao evento original")
    return original


def validate_capture(folder):
    required = {
        "attribute-source.jsonl", "logic-engine.jsonl",
        "rule-executor.jsonl", "attribute-event-original.json",
        "capture-summary.json",
    }
    files = {p.name for p in folder.iterdir() if p.is_file()}
    if files != required | {"checksums.sha256"}:
        raise ValueError("inventario da captura E08-D17E divergente")
    hashes = (folder / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    checked = set()
    for line in hashes:
        if len(line) < 67 or line[64:66] != "  ":
            raise ValueError("manifesto SHA-256 invalido")
        digest, filename = line[:64], line[66:]
        if filename not in required or filename in checked:
            raise ValueError("arquivo do manifesto ausente ou duplicado")
        if sha256_file(folder / filename) != digest.lower():
            raise ValueError(f"hash divergente na captura: {filename}")
        checked.add(filename)
    if checked != required:
        raise ValueError("manifesto da captura incompleto")
    info = json.loads((folder / "capture-summary.json").read_text(encoding="utf-8"))
    if any((info.get("status") != "CAPTURED",
            info.get("event_id") != EVENT_ID,
            info.get("send_count") != 1,
            info.get("ack_count") != 1,
            info.get("receive_count") != 1,
            info.get("payloads_equal") is not True,
            info.get("effects_logged") != 0)):
        raise ValueError("captura E08-D17E nao esta aprovada")
    return validate_original(json.loads(
        (folder / "attribute-event-original.json").read_text(encoding="utf-8")
    ))


def read_logs():
    logs, parsed = {}, {}
    for role in ROLES:
        raw = call("docker", "logs", CONTAINERS[role])
        logs[role] = raw
        parsed[role] = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return logs, parsed


def matches(records, event_type, path, original):
    return [r for r in records if r.get("event_type") == event_type
            and r.get("path") == path and r.get("payload") == original]


def assert_original_logs(parsed, original):
    source = parsed["attribute-source"]
    logic = parsed["logic-engine"]
    executor = parsed["rule-executor"]
    sends = matches(source, "send", "/notifications/attribute", original)
    acks = matches(source, "ack", "/notifications/attribute", original)
    received = matches(logic, "mutation", "/notifications/attribute", original)
    if len(sends) != 1 or len(acks) != 1 or len(received) != 1:
        raise ValueError("V05 parece ja reenviado ou logs originais divergentes")
    if acks[0].get("response") != {"accepted": True, "duplicate": False}:
        raise ValueError("ACK original divergente")
    if received[0].get("status") != 200 or received[0].get("response") != {
        "accepted": True, "duplicate": False
    }:
        raise ValueError("recebimento original divergente")
    if any(e.get("event_type") == "effect" for e in executor):
        raise ValueError("ja existem efeitos no executor")


def topology():
    network = json.loads(call("docker", "network", "inspect", NETWORK))[0]
    if network["Driver"] != "bridge" or network["Internal"] is not True:
        raise ValueError("rede V05 inesperada")
    img = json.loads(call("docker", "image", "inspect", BASE_IMAGE))[0]
    if (img["Os"] != "linux" or img["Architecture"] != "amd64"
            or img["Config"]["Labels"].get("org.opencontainers.image.revision") != BUILD_SHA):
        raise ValueError("imagem Docker divergente")
    meta, ids = {}, []
    for role in ROLES:
        info = json.loads(call("docker", "inspect", CONTAINERS[role]))[0]
        if (info["State"]["Running"] is not True
                or info["Image"] != img["Id"]
                or info["Config"]["Labels"].get("tcc2.test") != "V05"
                or NETWORK not in info["NetworkSettings"]["Networks"]
                or info["HostConfig"]["PortBindings"]):
            raise ValueError(f"conteiner V05 divergente: {role}")
        ids.append(info["Id"])
        meta[role] = {"name": CONTAINERS[role], "id": info["Id"],
                      "started_at": info["State"]["StartedAt"]}
    if len(set(ids)) != 3:
        raise ValueError("IDs Docker duplicados")
    return {"network": NETWORK, "internal": True, "image": BASE_IMAGE,
            "image_id": img["Id"], "image_revision": BUILD_SHA,
            "containers": meta}


def verify_after(before_state, after_state, before_logs, after_logs, original):
    if after_state != before_state:
        raise ValueError("um ou mais estados mudaram apos replay")
    for role in ("attribute-source", "rule-executor"):
        if before_logs[role] != after_logs[role]:
            raise ValueError(f"logs inesperadamente alterados: {role}")
    old, new = before_logs["logic-engine"], after_logs["logic-engine"]
    if len(new) != len(old) + 1 or new[:-1] != old:
        raise ValueError("quantidade ou ordem de logs do avaliador divergente")
    event = new[-1]
    if (event.get("event_type") != "mutation"
            or event.get("path") != "/notifications/attribute"
            or event.get("payload") != original
            or event.get("status") != 200
            or event.get("response") != {"accepted": True, "duplicate": True}):
        raise ValueError("log do replay idempotente divergente")


def execute(capture, output):
    if call("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("branch Git incorreta")
    if call("git", "status", "--porcelain").strip():
        raise ValueError("alteracoes Git locais: interrompido")
    if Path(output).exists():
        raise ValueError("pasta de evidencias ja existe; nao sobrescrever")

    original = validate_capture(Path(capture))
    manifest = topology()
    manifest["git_sha"] = call("git", "rev-parse", "HEAD").strip()
    manifest["capture_folder"] = str(capture)
    manifest["original_event_sha256"] = sha256_file(
        Path(capture) / "attribute-event-original.json"
    )
    before = read_states()
    assert_prepared(before)
    old_text, old_logs = read_logs()
    assert_original_logs(old_logs, original)

    # O preflight esta concluido; marcar a intencao ANTES do unico POST.
    folder = Path(output)
    folder.mkdir(parents=True, exist_ok=False)
    write_json(folder / "manifest.json", manifest)
    write_json(folder / "event-original.json", original)
    write_json(folder / "states-before.json", before)
    for role in ROLES:
        (folder / f"{role}-before.jsonl").write_text(old_text[role], encoding="utf-8")
    write_json(folder / "request-intent.json", {
        "target": CONTAINERS["logic-engine"],
        "path": "/notifications/attribute",
        "event_id": EVENT_ID, "attempt_count": 1,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "automatic_retry": False,
    })
    result = {"scenario": "C2", "criterion": "V05",
              "increment": "E08-D17F", "status": "FAIL",
              "replay_attempted": True, "event_id": EVENT_ID}
    try:
        answer = send_replay(original)
        write_json(folder / "replay-response.json", answer)
        post = read_states()
        write_json(folder / "states-after.json", post)
        next_text, next_logs = read_logs()
        verify_after(before, post, old_logs, next_logs, original)
        if answer != {"status": 200, "body": {"accepted": True, "duplicate": True}}:
            raise ValueError(f"ACK inesperado: {answer}")
        result["status"] = "PASS"
        result["state_unchanged"] = True
        result["new_logic_mutations"] = 1
        result["new_effects"] = 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError,
            subprocess.TimeoutExpired) as error:
        result["error"] = str(error)
    finally:
        for role in ROLES:
            try:
                raw = call("docker", "logs", CONTAINERS[role])
                (folder / f"{role}-after.jsonl").write_text(raw, encoding="utf-8")
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
                (folder / f"{role}-capture-error.txt").write_text(str(error), encoding="utf-8")
        write_json(folder / "validation.json", result)
        (folder / "checksums.sha256").write_text("".join(
            f"{sha256_file(p)}  {p.name}\n"
            for p in sorted(folder.iterdir()) if p.name != "checksums.sha256"
        ), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = execute(args.capture, args.output)
    except (OSError, ValueError, RuntimeError, KeyError, TypeError,
            subprocess.TimeoutExpired) as error:
        print("E08-D17F: ABORTADO NO PREFLIGHT:", str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("Evidencias:", args.output.resolve())
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
