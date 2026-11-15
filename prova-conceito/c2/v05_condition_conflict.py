"""E08-D17P: unica tentativa de conflito ConditionChanged em C2/V05.

Conserva event_id, timestamp, run_id e demais campos do evento real.
Altera apenas approved (True -> False), esperando 409 e estado invariavel.
Nenhum retry: em caso de erro apos a tentativa, preservar evidencias.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

from c0.runner import sha256_file, write_json
from c1.protocol import validate_condition_event
from c2.v03_cold import POST
from c2.v05_condition_first import CONDITION_ID, ATTRIBUTE_ID, EFFECT_ID, check_hashes
from c2.v05_condition_replay import SOURCE_SHA256, PATH
from c2.v05_duplicate import ROLES, CONTAINERS, topology, call, read_states, read_logs

EXPECTED_ERROR = "event_id reutilizado com payload diferente"
REPLAY_FILES = {
    "attribute-source-before.jsonl", "attribute-source-after.jsonl",
    "condition-event-original.json", "logic-engine-before.jsonl",
    "logic-engine-after.jsonl", "manifest.json", "replay-response.json",
    "request-intent.json", "rule-executor-before.jsonl",
    "rule-executor-after.jsonl", "states-before.json", "states-after.json",
    "validation.json",
}


def conflict_event(original):
    validate_condition_event(original)
    if (original.get("event_id") != CONDITION_ID
            or original.get("caused_by") != ATTRIBUTE_ID
            or original.get("approved") is not True
            or sha256_json_event_unchanged(original) is False):
        raise ValueError("ConditionChanged V05 original inesperada")
    result = dict(original)
    result["approved"] = False
    validate_condition_event(result)
    if set(result) != set(original) or sum(
        result[k] != original[k] for k in original
    ) != 1:
        raise ValueError("conflito deve alterar somente approved")
    return result


def sha256_json_event_unchanged(original):
    # O hash do arquivo original, e nao o JSON reserializado,
    # sera confirmado em preflight_previous().
    return original["event_id"] == CONDITION_ID


def assert_conflict_reply(reply):
    if reply != {"status": 409, "body": {"error": EXPECTED_ERROR}}:
        raise ValueError("resposta HTTP de conflito divergente")


def verify_conflict(before, after, before_logs, after_logs, conflict):
    if before != after:
        raise ValueError("conflito alterou estado funcional")
    for role in ("attribute-source", "logic-engine"):
        if before_logs[role] != after_logs[role]:
            raise ValueError("logs indevidamente alterados: " + role)
    old, new = before_logs["rule-executor"], after_logs["rule-executor"]
    if len(new) != len(old) + 1 or new[:len(old)] != old:
        raise ValueError("quantidade/ordem de logs do executor divergente")
    entry = new[-1]
    if (entry.get("event_type") != "mutation"
            or entry.get("path") != PATH
            or entry.get("status") != 409
            or entry.get("payload") != conflict
            or entry.get("response") != {"error": EXPECTED_ERROR}):
        raise ValueError("log do conflito de condicao divergente")
    if after["rule-executor"]["effects"] != before["rule-executor"]["effects"]:
        raise ValueError("conflito produziu efeito adicional")


def preflight_previous(previous, meta, current_states, raw_logs, parsed_logs):
    folder = check_hashes(previous, REPLAY_FILES)
    original_file = folder / "condition-event-original.json"
    if sha256_file(original_file) != SOURCE_SHA256:
        raise ValueError("hash do ConditionChanged original divergente")
    original = json.loads(original_file.read_text(encoding="utf-8"))
    conflict_event(original)  # exige contrato valido e diferenca unica
    validation = json.loads(
        (folder / "validation.json").read_text(encoding="utf-8"))
    response = json.loads(
        (folder / "replay-response.json").read_text(encoding="utf-8"))
    saved_meta = json.loads(
        (folder / "manifest.json").read_text(encoding="utf-8"))
    saved_state = json.loads(
        (folder / "states-after.json").read_text(encoding="utf-8"))
    before_saved_state = json.loads(
        (folder / "states-before.json").read_text(encoding="utf-8"))
    if (validation.get("status") != "PASS"
            or validation.get("increment") != "E08-D17M"
            or validation.get("criterion") != "V05"
            or validation.get("event_id") != CONDITION_ID
            or validation.get("duplicate") is not True
            or validation.get("state_unchanged") is not True
            or validation.get("new_effects") != 0
            or validation.get("new_executor_mutations") != 1
            or response != {"status": 200, "body": {
                "accepted": True, "duplicate": True
            }}):
        raise ValueError("replay E08-D17M anterior nao validado")
    if current_states != saved_state or saved_state != before_saved_state:
        raise ValueError("estados V05 divergentes do replay auditado")
    executor = current_states["rule-executor"]
    if (executor["ready"] is not True
            or executor["faulted"] is not False
            or executor["approved"] is not True
            or executor["condition_sequence"] != 1
            or executor["received_ids"] != [CONDITION_ID]
            or len(executor["effects"]) != 1
            or executor["effects"][0]["event_id"] != EFFECT_ID):
        raise ValueError("executor V05 nao esta no estado auditado")
    for key in ("network", "internal", "image", "image_id", "image_revision"):
        if meta[key] != saved_meta[key]:
            raise ValueError("topologia/imagem divergente: " + key)
    for role in ROLES:
        if meta["containers"][role] != saved_meta["containers"][role]:
            raise ValueError("conteiner V05 reiniciado/substituido: " + role)
        if raw_logs[role] != (
            folder / f"{role}-after.jsonl").read_text(encoding="utf-8"):
            raise ValueError("logs V05 divergentes: " + role)
    if {role: len(parsed_logs[role]) for role in ROLES} != {
        "attribute-source": 10, "logic-engine": 10, "rule-executor": 5
    }:
        raise ValueError("contagem dos logs V05 inesperada")
    last = parsed_logs["rule-executor"][-1]
    if (last.get("event_type") != "mutation" or last.get("path") != PATH
            or last.get("payload") != original
            or last.get("status") != 200
            or last.get("response") != {"accepted": True, "duplicate": True}):
        raise ValueError("replay de condicao nao e o ultimo registro")
    return original, sha256_file(folder / "validation.json")


def execute(previous, output):
    if call("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("branch Git incorreta")
    if call("git", "status", "--porcelain").strip():
        raise ValueError("alteracoes locais no Git")
    folder = Path(output)
    if folder.exists():
        raise ValueError("pasta de evidencias ja existe; nao sobrescrever")
    meta = topology()
    before = read_states()
    old_text, old_logs = read_logs()
    original, previous_sha = preflight_previous(
        Path(previous), meta, before, old_text, old_logs)
    changed = conflict_event(original)

    # A partir daqui os arquivos sao escritos ANTES do unico POST.
    folder.mkdir(parents=True, exist_ok=False)
    meta["git_sha"] = call("git", "rev-parse", "HEAD").strip()
    meta["previous_validation_sha256"] = previous_sha
    meta["original_condition_sha256"] = SOURCE_SHA256
    meta["preflight_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(folder / "manifest.json", meta)
    write_json(folder / "event-original.json", original)
    write_json(folder / "event-conflict.json", changed)
    write_json(folder / "states-before.json", before)
    for role in ROLES:
        (folder / f"{role}-before.jsonl").write_text(
            old_text[role], encoding="utf-8")
    write_json(folder / "request-intent.json", {
        "target": CONTAINERS["rule-executor"], "path": PATH,
        "event_id": CONDITION_ID, "changed_field": "approved",
        "previous_value": True, "conflicting_value": False,
        "attempt_count": 1, "automatic_retry": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    })
    result = {
        "scenario": "C2", "criterion": "V05",
        "increment": "E08-D17P", "status": "FAIL",
        "attempted": True, "event_id": CONDITION_ID,
    }
    try:
        # UMA UNICA tentativa. Mesmo em timeout/erro, NAO repetir.
        reply = json.loads(call(
            "docker", "exec", CONTAINERS["rule-executor"],
            "python", "-c", POST, PATH,
            json.dumps(changed, sort_keys=True, ensure_ascii=True),
            "application/json"))
        write_json(folder / "conflict-response.json", reply)
        assert_conflict_reply(reply)
        after = read_states()
        write_json(folder / "states-after.json", after)
        _, new_logs = read_logs()
        verify_conflict(before, after, old_logs, new_logs, changed)
        result.update(status="PASS", expected_http=409,
                      observed_http=409, state_unchanged=True,
                      new_effects=0, new_executor_mutations=1)
    except (OSError, RuntimeError, ValueError, TypeError, KeyError,
            subprocess.TimeoutExpired) as error:
        result["error"] = str(error)
    finally:
        if not (folder / "states-after.json").exists():
            try:
                write_json(folder / "states-after.json", read_states())
            except (OSError, RuntimeError, ValueError, TypeError, KeyError,
                    subprocess.TimeoutExpired) as error:
                (folder / "state-capture-error.txt").write_text(
                    str(error), encoding="utf-8")
        for role in ROLES:
            try:
                raw = call("docker", "logs", CONTAINERS[role])
                (folder / f"{role}-after.jsonl").write_text(
                    raw, encoding="utf-8")
            except (OSError, RuntimeError, ValueError, TypeError, KeyError,
                    subprocess.TimeoutExpired) as error:
                (folder / f"{role}-capture-error.txt").write_text(
                    str(error), encoding="utf-8")
        write_json(folder / "validation.json", result)
        (folder / "checksums.sha256").write_text(
            "".join(f"{sha256_file(file)}  {file.name}\n"
                    for file in sorted(folder.iterdir())
                    if file.is_file() and file.name != "checksums.sha256"),
            encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = execute(args.previous, args.output)
    except (OSError, RuntimeError, ValueError, TypeError, KeyError,
            subprocess.TimeoutExpired) as error:
        print("E08-D17P: ABORTADO NO PREFLIGHT:", error, file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("Evidencias:", args.output.resolve())
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
