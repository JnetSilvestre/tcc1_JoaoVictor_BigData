"""E08-D17K — primeira transicao de condicao no C2/V05 (um unico POST).

Aborta no preflight em caso de estado inesperado; registra intencao ANTES do
POST. Nunca aplica retry. Se o POST falhar, preservar evidencias e investigar.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

from c0.runner import sha256_file, write_json
from c1.protocol import validate_attribute_event, validate_condition_event
from c2.v03_cold import POST
from c2.v05_duplicate import (
    ROLES, CONTAINERS, RUN_ID, SNAPSHOT, EVENT_ID,
    assert_prepared, call, validate_capture, topology, read_logs, read_states,
)
from c2.v05_conflict import check_previous

ATTRIBUTE_ID = f"{RUN_ID}:atB:1"
CONDITION_ID = f"{RUN_ID}:cn1:1"
EFFECT_ID = f"{RUN_ID}:rl1:1"
CHANGE = {"run_id": RUN_ID, "request_id": "v05-req-atB-1",
          "entity_id": "atB", "value": 1, "step": 2}
CONFLICT_FILES = {
    "attribute-source-before.jsonl", "attribute-source-after.jsonl",
    "logic-engine-before.jsonl", "logic-engine-after.jsonl",
    "rule-executor-before.jsonl", "rule-executor-after.jsonl",
    "states-before.json", "states-after.json", "event-original.json",
    "event-conflict.json", "conflict-response.json", "request-intent.json",
    "manifest.json", "validation.json",
}


def check_hashes(folder, expected):
    folder = Path(folder)
    if not folder.is_dir():
        raise ValueError("pasta de conflito anterior ausente")
    files = {p.name for p in folder.iterdir() if p.is_file()}
    if files != expected | {"checksums.sha256"}:
        raise ValueError("inventario anterior divergente")
    checked = set()
    for line in (folder / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([a-fA-F0-9]{64})  ([^/\\]+)", line)
        if not match:
            raise ValueError("linha SHA-256 invalida")
        sha, name = match.groups()
        if name not in expected or name in checked:
            raise ValueError("arquivo ausente ou repetido no manifesto")
        if sha256_file(folder / name) != sha.lower():
            raise ValueError("checksum divergente: " + name)
        checked.add(name)
    if checked != expected:
        raise ValueError("manifesto incompleto")
    return folder


def check_conflict(folder, original, docker_meta):
    folder = check_hashes(folder, CONFLICT_FILES)
    v = json.loads((folder / "validation.json").read_text(encoding="utf-8"))
    reply = json.loads((folder / "conflict-response.json").read_text(encoding="utf-8"))
    first = json.loads((folder / "event-original.json").read_text(encoding="utf-8"))
    changed = json.loads((folder / "event-conflict.json").read_text(encoding="utf-8"))
    meta = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if (v.get("status") != "PASS" or v.get("increment") != "E08-D17H"
            or v.get("observed_http") != 409 or v.get("state_unchanged") is not True
            or v.get("new_effects") != 0
            or reply != {"status": 409, "body": {"error": "event_id reutilizado com payload diferente"}}
            or first != original or changed != {**original, "value": 6}):
        raise ValueError("evidencia anterior do conflito nao aprovada")
    if (folder / "states-before.json").read_bytes() != (folder / "states-after.json").read_bytes():
        raise ValueError("conflito anterior modificou estado")
    for role in ROLES:
        old = meta["containers"][role]
        current = docker_meta["containers"][role]
        if old["id"] != current["id"] or old["started_at"] != current["started_at"]:
            raise ValueError("conteiner V05 reiniciado desde a rodada anterior")
    return sha256_file(folder / "validation.json")


def preflight_logs(logs, original):
    source = [r for r in logs["attribute-source"]
              if r.get("event_type") == "send"
              and r.get("path") == "/notifications/attribute"]
    received = [r for r in logs["logic-engine"]
                if r.get("event_type") == "mutation"
                and r.get("path") == "/notifications/attribute"]
    condition = [r for r in logs["logic-engine"]
                 if r.get("path") == "/notifications/condition"]
    if len(source) != 1 or source[0].get("payload") != original:
        raise ValueError("envio original da fonte nao e unico")
    if len(received) != 3 or condition:
        raise ValueError("avaliador ja processou evento inesperado")
    statuses = (200, 200, 409)
    responses = (
        {"accepted": True, "duplicate": False},
        {"accepted": True, "duplicate": True},
        {"error": "event_id reutilizado com payload diferente"},
    )
    for event, status, response, value in zip(received, statuses, responses, (5, 5, 6)):
        if (event.get("status") != status or event.get("response") != response
                or event.get("payload") != {**original, "value": value}):
            raise ValueError("historico de AttributeChanged inesperado")
    if any(r.get("event_type") == "effect" for r in logs["rule-executor"]):
        raise ValueError("executor ja executou um efeito")


def assert_change_response(response):
    if response != {"status": 200, "body": {
            "changed": True, "sequence": 1,
            "event_id": ATTRIBUTE_ID, "duplicate_request": False}}:
        raise ValueError("resposta HTTP de atB inesperada: " + str(response))


def expected_effect():
    return {
        "schema_version": 1, "run_id": RUN_ID, "event_id": EFFECT_ID,
        "entity_id": "rl1", "step": 2, "caused_by": CONDITION_ID,
        "attribute_event_id": ATTRIBUTE_ID, "effect": "executed",
    }


def validate_after(states):
    for role, s in states.items():
        if not (s.get("service") == role and s.get("ready") is True
                and s.get("run_id") == RUN_ID
                and s.get("snapshot_version") == SNAPSHOT):
            raise ValueError("estado ou snapshot inesperado apos o POST")
    source, logic, executor = (states[role] for role in ROLES)
    attributes, sequences = {"atA": 5, "atB": 1}, {"atA": 1, "atB": 1}
    if (source.get("attributes") != attributes
            or source.get("sequences") != sequences
            or source.get("pending_request_id") is not None):
        raise ValueError("attribute-source nao concluiu atB")
    events = logic.get("condition_events")
    if (logic.get("attributes") != attributes
            or logic.get("sequences") != sequences
            or logic.get("received_ids") != [EVENT_ID, ATTRIBUTE_ID]
            or logic.get("condition") is not True
            or logic.get("condition_sequence") != 1
            or logic.get("faulted") is not False
            or not isinstance(events, list) or len(events) != 1):
        raise ValueError("logic-engine nao produziu a transicao prevista")
    condition = events[0]
    validate_condition_event(condition)
    required = {
        "schema_version": 1, "event_id": CONDITION_ID,
        "run_id": RUN_ID, "source": "logic-engine",
        "entity_id": "cn1", "sequence": 1, "approved": True,
        "caused_by": ATTRIBUTE_ID, "step": 2,
    }
    if (set(condition) != set(required) | {"emitted_at"}
            or any(condition.get(k) != value for k, value in required.items())):
        raise ValueError("payload original de ConditionChanged inesperado")
    effect = expected_effect()
    if (executor.get("approved") is not True
            or executor.get("condition_sequence") != 1
            or executor.get("received_ids") != [CONDITION_ID]
            or executor.get("effects") != [effect]
            or executor.get("faulted") is not False):
        raise ValueError("executor nao realizou exatamente um efeito")
    return condition, effect


def verify_logs(before, after, condition, effect):
    counts = {"attribute-source": 3, "logic-engine": 3, "rule-executor": 2}
    for role in ROLES:
        old, new = before[role], after[role]
        if len(new) != len(old) + counts[role] or new[:len(old)] != old:
            raise ValueError("logs inesperados: " + role)
    source = after["attribute-source"][-3:]
    logic = after["logic-engine"][-3:]
    executor = after["rule-executor"][-2:]
    attr = source[0].get("payload")
    validate_attribute_event(attr)
    required_attr = {
        "schema_version": 1, "event_id": ATTRIBUTE_ID,
        "run_id": RUN_ID, "source": "attribute-source",
        "entity_id": "atB", "sequence": 1, "value": 1,
        "request_id": CHANGE["request_id"], "step": 2,
    }
    if (set(attr) != set(required_attr) | {"emitted_at"}
            or any(attr.get(k) != v for k, v in required_attr.items())):
        raise ValueError("evento original AttributeChanged inesperado")
    ack = {"accepted": True, "duplicate": False}
    if not (
        source[0].get("event_type") == "send"
        and source[0].get("path") == "/notifications/attribute"
        and source[1].get("event_type") == "ack"
        and source[1].get("payload") == attr
        and source[1].get("response") == ack
        and source[2].get("event_type") == "mutation"
        and source[2].get("path") == "/attributes/change"
        and source[2].get("payload") == CHANGE
        and source[2].get("status") == 200
        and logic[0].get("event_type") == "send"
        and logic[0].get("path") == "/notifications/condition"
        and logic[0].get("payload") == condition
        and logic[1].get("event_type") == "ack"
        and logic[1].get("path") == "/notifications/condition"
        and logic[1].get("payload") == condition
        and logic[1].get("response") == ack
        and logic[2].get("event_type") == "mutation"
        and logic[2].get("path") == "/notifications/attribute"
        and logic[2].get("payload") == attr
        and logic[2].get("status") == 200
        and logic[2].get("response") == ack
        and executor[0].get("event_type") == "effect"
        and executor[0].get("payload") == effect
        and executor[1].get("event_type") == "mutation"
        and executor[1].get("path") == "/notifications/condition"
        and executor[1].get("payload") == condition
        and executor[1].get("status") == 200
        and executor[1].get("response") == ack
    ):
        raise ValueError("cadeia de logs HTTP/efeito inesperada")
    return attr


def execute(capture, previous, conflict, output):
    if call("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("branch Git incorreta")
    if call("git", "status", "--porcelain").strip():
        raise ValueError("alteracoes locais de Git")
    folder = Path(output)
    if folder.exists():
        raise ValueError("diretorio de evidencias ja existe")
    original = validate_capture(Path(capture))
    prior_duplicate_hash = check_previous(Path(previous), original)
    meta = topology()
    prior_conflict_hash = check_conflict(Path(conflict), original, meta)
    before = read_states()
    assert_prepared(before)
    old_text, old_logs = read_logs()
    preflight_logs(old_logs, original)

    folder.mkdir(parents=True, exist_ok=False)
    meta.update({
        "git_sha": call("git", "rev-parse", "HEAD").strip(),
        "previous_duplicate_validation_sha256": prior_duplicate_hash,
        "previous_conflict_validation_sha256": prior_conflict_hash,
        "original_capture_sha256": sha256_file(
            Path(capture) / "attribute-event-original.json"),
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    })
    write_json(folder / "manifest.json", meta)
    write_json(folder / "states-before.json", before)
    for role in ROLES:
        (folder / f"{role}-before.jsonl").write_text(
            old_text[role], encoding="utf-8")
    write_json(folder / "request-intent.json", {
        "target": CONTAINERS["attribute-source"],
        "path": "/attributes/change", "payload": CHANGE,
        "attempt_count": 1, "automatic_retry": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    })
    result = {"scenario": "C2", "criterion": "V05",
              "increment": "E08-D17K", "status": "FAIL",
              "attempted": True, "expected_change": CHANGE}
    try:
        # UM UNICO POST — nao repetir se ocorrer erro/timeout.
        response = json.loads(call(
            "docker", "exec", CONTAINERS["attribute-source"], "python", "-c",
            POST, "/attributes/change", json.dumps(CHANGE, sort_keys=True),
            "application/json",
        ))
        write_json(folder / "attribute-response.json", response)
        assert_change_response(response)
        after = read_states()
        write_json(folder / "states-after.json", after)
        condition, effect = validate_after(after)
        _, new_logs = read_logs()
        attr = verify_logs(old_logs, new_logs, condition, effect)
        write_json(folder / "attribute-event-original.json", attr)
        write_json(folder / "condition-event-original.json", condition)
        result.update(status="PASS", condition_sequence=1, effects_count=1,
                      attribute_event_id=ATTRIBUTE_ID,
                      condition_event_id=CONDITION_ID, effect_id=EFFECT_ID)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError,
            subprocess.TimeoutExpired) as error:
        result["error"] = str(error)
    finally:
        for role in ROLES:
            try:
                text = call("docker", "logs", CONTAINERS[role])
                (folder / f"{role}-after.jsonl").write_text(text, encoding="utf-8")
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
                (folder / f"{role}-capture-error.txt").write_text(
                    str(error), encoding="utf-8")
        write_json(folder / "validation.json", result)
        (folder / "checksums.sha256").write_text("".join(
            f"{sha256_file(file)}  {file.name}\n"
            for file in sorted(folder.iterdir())
            if file.is_file() and file.name != "checksums.sha256"
        ), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("capture", "previous", "conflict", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    try:
        report = execute(args.capture, args.previous, args.conflict, args.output)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError,
            subprocess.TimeoutExpired) as error:
        print("E08-D17K: ABORTADO NO PREFLIGHT:", error, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("Evidencias:", args.output.resolve())
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
