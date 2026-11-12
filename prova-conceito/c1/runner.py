"""Executa a fixture C1 em três processos e preserva as evidências da rodada."""

import argparse
from contextlib import ExitStack
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from c0.io import read_jsonl, validate_input, write_jsonl
from c0.runner import PROJECT_ROOT, compare_effects, git_sha, sha256_file, write_json
from .client import ResponseError, request
from .protocol import utc_now
from .service import ROLES


def stop(process):
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def start_services(output, stack):
    ports = {}
    for role in reversed(ROLES):
        log = output / f"{role}.jsonl"
        command = [sys.executable, "-m", "c1.service", role]
        if ports:
            command.extend(["--downstream-port", str(downstream)])
        with log.open("wb") as stdout, (output / f"{role}.stderr.log").open("wb") as stderr:
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr, cwd=PROJECT_ROOT)
        stack.callback(stop, process)

        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            first_line, newline, _ = log.read_bytes().partition(b"\n")
            if newline:
                startup = json.loads(first_line)
                if startup["pid"] != process.pid or startup["service"] != role:
                    raise RuntimeError(f"identidade inesperada: {startup}")
                downstream = ports[role] = startup["port"]
                break
            if process.poll() is not None:
                raise RuntimeError(f"{role} saiu com código {process.returncode}")
            time.sleep(0.05)
        else:
            raise RuntimeError(f"{role} não anunciou a porta")
    return ports


def exercise(ports, rows, output):
    source, logic, executor = ROLES
    changes = [{key: value for key, value in row.items() if key != "seed"} for row in rows]
    checks = {}

    with (output / "http.jsonl").open("w", encoding="utf-8") as transcript:
        def call(role, path, payload=None, expected=200):
            try:
                body = request(ports[role], path, payload)
                status = 200
            except ResponseError as error:
                status, body = error.status, error.body
            print(json.dumps({
                "timestamp": utc_now(), "service": role, "path": path,
                "payload": payload, "status": status, "response": body,
            }), file=transcript, flush=True)
            if status != expected:
                raise RuntimeError(f"{role} {path}: esperado {expected}, recebido {status}: {body}")
            return body

        def states():
            return {role: call(role, "/state") for role in ROLES}

        pids = {role: call(role, "/health/live")["pid"] for role in ROLES}
        for role in ROLES:
            call(role, "/health/ready", expected=503)
        cold = states()
        call(source, "/attributes/change", changes[0], expected=409)
        checks["cold_change_preserved_state"] = states() == cold
        run_id = rows[0]["run_id"]
        call(source, "/init/snapshot", {"run_id": run_id})
        for role in ROLES:
            call(role, "/health/ready")
        initial = states()
        checks["snapshot"] = (
            all(state["snapshot_version"] == f"{run_id}:snapshot:0" and state["run_id"] == run_id
                for state in initial.values())
            and all(initial[role]["attributes"] == {"atA": 0, "atB": 0}
                    and initial[role]["sequences"] == {"atA": 0, "atB": 0}
                    for role in (source, logic))
            and initial[logic]["condition"] is False and initial[executor]["approved"] is False
            and initial[logic]["condition_sequence"] == initial[executor]["condition_sequence"] == 0
            and initial[executor]["effects"] == []
        )
        for bad in ({}, {**changes[0], "value": True}, {**changes[0], "entity_id": "unknown"}):
            call(source, "/attributes/change", bad, expected=422)
        checks["invalid_preserved_state"] = states() == initial

        for change in changes:
            call(source, "/attributes/change", change)
        final = states()

        source_log = read_jsonl(output / f"{source}.jsonl")
        logic_log = read_jsonl(output / f"{logic}.jsonl")
        attributes = [row["payload"] for row in source_log
                      if row["event_type"] == "send" and row["path"] == "/notifications/attribute"]
        conditions = final[logic]["condition_events"]
        executor_log = read_jsonl(output / f"{executor}.jsonl")
        checks["transport"] = (
            len(set(pids.values())) == 3
            and all(row["pid"] == pids[role] and row["service"] == role
                    for role, log in zip(ROLES, (source_log, logic_log, executor_log))
                    for row in log)
            and [event["event_id"] for event in attributes] == final[logic]["received_ids"]
            and [event["event_id"] for event in conditions] == final[executor]["received_ids"]
            and [row["payload"] for row in logic_log
                 if row["event_type"] == "mutation" and row["path"] == "/notifications/attribute"]
            == attributes
            and [row["payload"] for row in executor_log
                 if row["event_type"] == "mutation" and row["path"] == "/notifications/condition"]
            == conditions
            and [row["payload"] for row in executor_log if row["event_type"] == "effect"]
            == final[executor]["effects"]
        )
        duplicate_request = call(source, "/attributes/change", changes[-1])
        checks["duplicate_request"] = duplicate_request["duplicate_request"]
        for role, path, events in (
            (logic, "/notifications/attribute", attributes),
            (executor, "/notifications/condition", conditions),
        ):
            first, last = events[0], events[-1]
            checks[f"{role}_duplicate"] = call(role, path, first)["duplicate"]
            conflict = {**first, "emitted_at": utc_now()}
            call(role, path, conflict, expected=409)
            sequence = last["sequence"] + 2
            call(role, path, {**last, "sequence": sequence,
                              "event_id": f"{run_id}:{last['entity_id']}:{sequence}"}, expected=409)
        call(logic, "/notifications/attribute", {**attributes[0], "schema_version": 2}, expected=422)
        checks["replays_gaps_and_invalid_preserved_state"] = states() == final

    return checks, pids, initial, final


def run(output):
    output.mkdir(parents=True)
    fixture = PROJECT_ROOT / "fixtures" / "c0_minimo.jsonl"
    expected_file = PROJECT_ROOT / "fixtures" / "c0_esperado.jsonl"
    rows = read_jsonl(fixture)
    run_id, seed = validate_input(rows)
    expected = read_jsonl(expected_file)
    c0, execution, oracle = compare_effects(rows, expected)
    manifest = {
        "scenario": "C1", "run_id": run_id, "seed": seed,
        "timestamp": utc_now(), "git_sha": git_sha(),
        "python": platform.python_version(), "platform": platform.platform(),
        "fixture_sha256": sha256_file(fixture), "expected_sha256": sha256_file(expected_file),
    }
    report = {"scenario": "C1", "run_id": run_id, "status": "FAIL"}
    try:
        with ExitStack() as stack:
            ports = start_services(output, stack)
            checks, pids, initial, final = exercise(ports, rows, output)
        source, logic, executor = (final[role] for role in ROLES)
        effects = executor["effects"]
        checks.update({
            "matches_c0": c0["status"] == "PASS" and effects == execution["effects"],
            "matches_manual": effects == expected,
            "matches_oracle": effects == oracle,
            "matches_c0_state": (
                source["attributes"] == logic["attributes"] == {name: execution["final_state"][name] for name in ("atA", "atB")}
                and source["sequences"] == logic["sequences"] == execution["attribute_sequences"]
                and logic["condition_sequence"] == executor["condition_sequence"]
                == execution["condition_sequence"]
                and logic["condition"] == executor["approved"] == execution["final_state"]["condition"]
            ),
        })
        manifest.update({"ports": ports, "pids": pids})
        report.update({
            "checks": checks, "steps": [effect["step"] for effect in effects],
            "status": "PASS" if all(checks.values()) else "FAIL",
        })
        write_jsonl(output / "effects.jsonl", effects)
        write_jsonl(output / "c0-effects.jsonl", execution["effects"])
        write_jsonl(output / "oracle_independente.jsonl", oracle)
        write_json(output / "states.json", {"initial": initial, "final": final})
    except (OSError, ValueError, RuntimeError, ResponseError) as error:
        report["error"] = str(error)
    write_json(output / "validation.json", report)
    write_json(output / "manifest.json", manifest)
    (output / "checksums.sha256").write_text("".join(
        f"{sha256_file(path)}  {path.name}\n"
        for path in sorted(output.iterdir()) if path.name != "checksums.sha256"
    ), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="diretório novo para a rodada")
    args = parser.parse_args()
    try:
        report = run(args.output)
    except OSError as error:
        print(error, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
