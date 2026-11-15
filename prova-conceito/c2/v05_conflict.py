"""E08-D17H: uma tentativa de event_id conflitante em C2/V05.

Altera APENAS o campo 'value' de uma copia do AttributeChanged original.
Reenvia uma vez ao logic-engine, esperando HTTP 409 e estados invariaveis.
Antes do POST verifica eventos anteriores, topologia, checksum e ledger.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

from c0.runner import sha256_file, write_json
from c1.protocol import validate_attribute_event
from c2.v03_cold import POST
from c2.v05_duplicate import (
    ROLES, CONTAINERS, EVENT_ID, RUN_ID, SNAPSHOT,
    assert_prepared, call, validate_capture, topology, read_logs, read_states,
)

TARGET_PATH = "/notifications/attribute"
EXPECTED_ERROR = "event_id reutilizado com payload diferente"


def conflict_event(original):
    result = dict(original)
    if result["entity_id"] != "atA" or result["value"] != 5:
        raise ValueError("evento fonte nao corresponde ao V05 preparado")
    result["value"] = 6
    validate_attribute_event(result)
    if sum(result.get(k) != original.get(k) for k in set(result) | set(original)) != 1:
        raise ValueError("conflito deve mudar somente o valor")
    return result


def check_previous(folder, original):
    folder = Path(folder)
    if not folder.is_dir():
        raise ValueError("evidencias E08-D17F ausentes")
    manifest = folder / "checksums.sha256"
    if not manifest.is_file():
        raise ValueError("checksums E08-D17F ausentes")
    expected = {p.name for p in folder.iterdir() if p.is_file()} - {"checksums.sha256"}
    checked = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]{64})  ([^/\\]+)", line)
        if not match:
            raise ValueError("manifesto E08-D17F malformado")
        sha, name = match.groups()
        if name not in expected or name in checked:
            raise ValueError("arquivo E08-D17F ausente/duplicado")
        if sha256_file(folder / name) != sha.lower():
            raise ValueError("checksum divergente em E08-D17F: " + name)
        checked.add(name)
    if checked != expected:
        raise ValueError("manifesto E08-D17F incompleto")
    v = json.loads((folder / "validation.json").read_text(encoding="utf-8"))
    response = json.loads((folder / "replay-response.json").read_text(encoding="utf-8"))
    past = json.loads((folder / "event-original.json").read_text(encoding="utf-8"))
    if (v.get("status") != "PASS"
            or v.get("criterion") != "V05"
            or v.get("event_id") != EVENT_ID
            or v.get("state_unchanged") is not True
            or response != {"status": 200, "body": {"accepted": True, "duplicate": True}}
            or past != original):
        raise ValueError("replay E08-D17F anterior nao esta comprovado")
    return sha256_file(folder / "validation.json")


def previous_events(logs, original):
    rows = [
        event for event in logs["logic-engine"]
        if event.get("event_type") == "mutation"
        and event.get("path") == TARGET_PATH
    ]
    if len(rows) != 2:
        raise ValueError("esperadas duas notificacoes anteriores no avaliador")
    for i, duplicate in enumerate((False, True)):
        item = rows[i]
        if (item.get("payload") != original
                or item.get("status") != 200
                or item.get("response") != {"accepted": True, "duplicate": duplicate}):
            raise ValueError("historico do evento V05 foi alterado")
    if any(e.get("event_type") == "effect" for e in logs["rule-executor"]):
        raise ValueError("efeitos inesperados antes do conflito")
    if any(e.get("event_type") == "mutation"
           and e.get("path") == TARGET_PATH
           and e.get("status") == 409 for e in logs["logic-engine"]):
        raise ValueError("ja existe conflito anterior; nao repetir")


def check_conflict_reply(response):
    if response.get("status") != 409:
        raise ValueError("HTTP conflitante diferente de 409")
    body = response.get("body")
    if not isinstance(body, dict) or body.get("error") != EXPECTED_ERROR:
        raise ValueError("corpo de erro nao corresponde ao contrato")


def verify_after(before, after, logs_before, logs_after, conflict):
    if before != after:
        raise ValueError("estado global alterado pelo conflito")
    if logs_before["attribute-source"] != logs_after["attribute-source"]:
        raise ValueError("logs source alterados")
    if logs_before["rule-executor"] != logs_after["rule-executor"]:
        raise ValueError("logs executor alterados")
    old = logs_before["logic-engine"]
    new = logs_after["logic-engine"]
    if len(new) != len(old) + 1 or new[:-1] != old:
        raise ValueError("quantidade/ordem dos logs de logic-engine inesperada")
    event = new[-1]
    if (event.get("event_type") != "mutation"
            or event.get("path") != TARGET_PATH
            or event.get("payload") != conflict
            or event.get("status") != 409
            or event.get("response") != {"error": EXPECTED_ERROR}):
        raise ValueError("log do conflito inesperado")


def execute(capture, previous, output):
    if call("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("branch Git incorreta")
    if call("git", "status", "--porcelain").strip():
        raise ValueError("Git com alteracoes locais")
    if Path(output).exists():
        raise ValueError("diretorio ja existe; nao sobrescrever")
    original = validate_capture(Path(capture))
    prior_hash = check_previous(previous, original)
    conflict = conflict_event(original)
    docker_info = topology()
    before = read_states()
    assert_prepared(before)
    old_text, old_log = read_logs()
    previous_events(old_log, original)

    folder = Path(output)
    folder.mkdir(parents=True, exist_ok=False)
    docker_info["git_sha"] = call("git", "rev-parse", "HEAD").strip()
    docker_info["event_original_sha256"] = sha256_file(
        Path(capture) / "attribute-event-original.json")
    docker_info["previous_validation_sha256"] = prior_hash
    write_json(folder / "manifest.json", docker_info)
    write_json(folder / "event-original.json", original)
    write_json(folder / "event-conflict.json", conflict)
    write_json(folder / "states-before.json", before)
    for role in ROLES:
        (folder / f"{role}-before.jsonl").write_text(
            old_text[role], encoding="utf-8")

    write_json(folder / "request-intent.json", {
        "path": TARGET_PATH, "target": CONTAINERS["logic-engine"],
        "event_id": EVENT_ID, "attempt_count": 1,
        "automatic_retry": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    })
    result = {"scenario": "C2", "criterion": "V05",
              "increment": "E08-D17H", "status": "FAIL",
              "attempted": True, "event_id": EVENT_ID}
    try:
        reply = json.loads(call(
            "docker", "exec", CONTAINERS["logic-engine"], "python", "-c", POST,
            TARGET_PATH, json.dumps(conflict, sort_keys=True), "application/json",
        ))
        write_json(folder / "conflict-response.json", reply)
        check_conflict_reply(reply)
        after = read_states()
        write_json(folder / "states-after.json", after)
        _, new_log = read_logs()
        verify_after(before, after, old_log, new_log, conflict)
        result.update(status="PASS", expected_http=409,
                      observed_http=409, state_unchanged=True,
                      new_logic_mutations=1, new_effects=0)
    except (ValueError, RuntimeError, KeyError, TypeError,
            OSError, subprocess.TimeoutExpired) as error:
        result["error"] = str(error)
    finally:
        for role in ROLES:
            try:
                raw = call("docker", "logs", CONTAINERS[role])
                (folder / f"{role}-after.jsonl").write_text(raw, encoding="utf-8")
            except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
                (folder / f"{role}-capture-error.txt").write_text(
                    str(error), encoding="utf-8")
        write_json(folder / "validation.json", result)
        (folder / "checksums.sha256").write_text(
            "".join(f"{sha256_file(p)}  {p.name}\n"
                    for p in sorted(folder.iterdir())
                    if p.is_file() and p.name != "checksums.sha256"),
            encoding="utf-8",
        )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = execute(args.capture, args.previous, args.output)
    except (ValueError, RuntimeError, KeyError, TypeError,
            OSError, subprocess.TimeoutExpired) as error:
        print("E08-D17H: ABORTADO NO PREFLIGHT:", error, file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("Evidencias:", args.output.resolve())
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
