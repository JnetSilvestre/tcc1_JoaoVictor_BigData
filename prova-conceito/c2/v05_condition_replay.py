"""TCC2 E08-D17M: replay unico de ConditionChanged em C2/V05.

Requer evidencia E08-D17K preservada, hashes validos e estado/logs intactos.
Sem retry. Caso o POST seja enviado e ocorra erro, NAO repetir o ensaio.
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
from c2.v05_duplicate import (
    ROLES, CONTAINERS, RUN_ID, SNAPSHOT, topology, call,
    read_states, read_logs,
)
from c2.v05_condition_first import (
    CONDITION_ID, EFFECT_ID, ATTRIBUTE_ID,
    check_hashes, validate_after,
)

SOURCE_SHA256 = "04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54"
EVIDENCE_FILES = {
    "attribute-event-original.json", "attribute-response.json",
    "attribute-source-before.jsonl", "attribute-source-after.jsonl",
    "condition-event-original.json",
    "logic-engine-before.jsonl", "logic-engine-after.jsonl",
    "manifest.json", "request-intent.json",
    "rule-executor-before.jsonl", "rule-executor-after.jsonl",
    "states-before.json", "states-after.json", "validation.json",
}
PATH = "/notifications/condition"


def preflight_previous(folder, docker_meta, current_states, current_logs_text):
    folder = check_hashes(folder, EVIDENCE_FILES)
    raw_event = folder / "condition-event-original.json"
    if sha256_file(raw_event) != SOURCE_SHA256:
        raise ValueError("hash da ConditionChanged original nao coincide com auditoria E08-D17L")
    condition = json.loads(raw_event.read_text(encoding="utf-8"))
    validate_condition_event(condition)
    if (condition.get("event_id") != CONDITION_ID
            or condition.get("caused_by") != ATTRIBUTE_ID
            or condition.get("approved") is not True):
        raise ValueError("ConditionChanged original divergente")

    v = json.loads((folder / "validation.json").read_text(encoding="utf-8"))
    reply = json.loads((folder / "attribute-response.json").read_text(encoding="utf-8"))
    prev_state = json.loads((folder / "states-after.json").read_text(encoding="utf-8"))
    prev_meta = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if (v.get("status") != "PASS"
            or v.get("increment") != "E08-D17K"
            or v.get("condition_sequence") != 1
            or v.get("effects_count") != 1
            or reply != {"status": 200, "body": {
                "changed": True, "sequence": 1,
                "event_id": ATTRIBUTE_ID, "duplicate_request": False
            }}):
        raise ValueError("transicao E08-D17K anterior nao aprovada")
    captured, effect = validate_after(prev_state)
    if captured != condition or effect["event_id"] != EFFECT_ID:
        raise ValueError("estado E08-D17K nao corresponde ao evento original")
    if current_states != prev_state:
        raise ValueError("bancada V05 diferente do estado final E08-D17K")
    for role in ROLES:
        current = docker_meta["containers"][role]
        previous = prev_meta["containers"][role]
        if (current["id"] != previous["id"]
                or current["started_at"] != previous["started_at"]):
            raise ValueError("conteiner V05 reiniciado/substituido: " + role)
        prior_log = (folder / f"{role}-after.jsonl").read_text(encoding="utf-8")
        if current_logs_text[role] != prior_log:
            raise ValueError("logs V05 divergentes antes do replay: " + role)
    return condition, sha256_file(folder / "validation.json")


def assert_replay_response(response):
    if response != {"status": 200, "body": {"accepted": True, "duplicate": True}}:
        raise ValueError("replay nao produziu ACK duplicado HTTP 200")


def validate_replay(before, after, old_logs, new_logs, condition):
    if before != after:
        raise ValueError("replay modificou estado funcional")
    for role in ("attribute-source", "logic-engine"):
        if new_logs[role] != old_logs[role]:
            raise ValueError("logs modificados fora do executor: " + role)
    old, new = old_logs["rule-executor"], new_logs["rule-executor"]
    if new[:len(old)] != old or len(new) != len(old) + 1:
        raise ValueError("executor nao acrescentou exatamente um registro")
    entry = new[-1]
    if (entry.get("event_type") != "mutation"
            or entry.get("path") != PATH
            or entry.get("payload") != condition
            or entry.get("status") != 200
            or entry.get("response") != {"accepted": True, "duplicate": True}):
        raise ValueError("log de replay nao corresponde ao ACK duplicado")
    if after["rule-executor"]["effects"] != before["rule-executor"]["effects"]:
        raise ValueError("houve efeitos duplicados")


def execute(previous, output):
    if call("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("branch Git incorreta")
    if call("git", "status", "--porcelain").strip():
        raise ValueError("Git possui alteracoes locais")
    folder = Path(output)
    if folder.exists():
        raise ValueError("pasta de evidencias ja existe")
    meta = topology()
    before = read_states()
    old_text, old_logs = read_logs()
    condition, previous_sha = preflight_previous(
        Path(previous), meta, before, old_text)

    # Todos os preflights terminam ANTES da criacao da pasta e do POST.
    folder.mkdir(parents=True, exist_ok=False)
    meta["git_sha"] = call("git", "rev-parse", "HEAD").strip()
    meta["previous_validation_sha256"] = previous_sha
    meta["condition_original_sha256"] = SOURCE_SHA256
    meta["preflight_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(folder / "manifest.json", meta)
    write_json(folder / "condition-event-original.json", condition)
    write_json(folder / "states-before.json", before)
    for role in ROLES:
        (folder / f"{role}-before.jsonl").write_text(
            old_text[role], encoding="utf-8")
    write_json(folder / "request-intent.json", {
        "target": CONTAINERS["rule-executor"],
        "path": PATH, "event_id": CONDITION_ID,
        "attempt_count": 1, "automatic_retry": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    })
    result = {
        "scenario": "C2", "criterion": "V05", "increment": "E08-D17M",
        "status": "FAIL", "replay_attempted": True, "event_id": CONDITION_ID,
    }
    try:
        # ESTE E O UNICO POST. Se ocorrer timeout/erro, NUNCA repetir.
        reply = json.loads(call(
            "docker", "exec", CONTAINERS["rule-executor"],
            "python", "-c", POST, PATH,
            json.dumps(condition, sort_keys=True, ensure_ascii=True),
            "application/json",
        ))
        write_json(folder / "replay-response.json", reply)
        assert_replay_response(reply)
        after = read_states()
        write_json(folder / "states-after.json", after)
        new_text, new_logs = read_logs()
        validate_replay(before, after, old_logs, new_logs, condition)
        result.update(status="PASS", expected_http=200,
                      observed_http=200, duplicate=True,
                      state_unchanged=True, new_effects=0,
                      new_executor_mutations=1)
    except (OSError, RuntimeError, ValueError, TypeError, KeyError,
            subprocess.TimeoutExpired) as error:
        result["error"] = str(error)
    finally:
        try:
            if not (folder / "states-after.json").exists():
                write_json(folder / "states-after.json", read_states())
        except (OSError, RuntimeError, ValueError, KeyError,
                subprocess.TimeoutExpired) as error:
            (folder / "state-capture-error.txt").write_text(str(error), encoding="utf-8")
        for role in ROLES:
            try:
                raw = call("docker", "logs", CONTAINERS[role])
                (folder / f"{role}-after.jsonl").write_text(
                    raw, encoding="utf-8")
            except (OSError, RuntimeError, ValueError,
                    subprocess.TimeoutExpired) as error:
                (folder / f"{role}-capture-error.txt").write_text(
                    str(error), encoding="utf-8")
        write_json(folder / "validation.json", result)
        (folder / "checksums.sha256").write_text(
            "".join(f"{sha256_file(file)}  {file.name}\n"
                    for file in sorted(folder.iterdir())
                    if file.is_file() and file.name != "checksums.sha256"),
            encoding="utf-8",
        )
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
        print("E08-D17M: ABORTADO NO PREFLIGHT:", error, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("Evidencias:", args.output.resolve())
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
