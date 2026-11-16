"""Validacao de corretude, integridade SHA256 e arquivamento por rodada."""
from datetime import datetime, timezone
import hashlib
import json
import csv
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from c0.oracle import calculate_expected_effects


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path, data):
    with Path(path).open("w", encoding="utf-8", newline="\n") as stream:
        for row in data:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_csv(path, rows, columns):
    """Representação derivada; JSONL continua sendo o dado bruto canônico."""
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def hash_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def check_run(rows, records, states):
    """Correcao da fixture completa; falha se qualquer resposta difere do contrato."""
    report = {"status": "FAIL", "checks": {}, "expected_effects": None}
    if not rows or len(records) != len(rows) + 1 or records[-1].get("type") != "summary":
        report["error"] = "quantidade de registros/summary incorreta"
        return report
    summary = records[-1]
    requests = records[:-1]
    values, sequences = {"atA": 0, "atB": 0}, {"atA": 0, "atB": 0}
    condition = False
    conditions = 0
    for row, actual in zip(rows, requests):
        name = row["entity_id"]
        changed = values[name] != row["value"]
        if changed:
            values[name] = row["value"]
            sequences[name] += 1
            approved = values["atA"] >= 5 and values["atB"] == 1
            if approved != condition:
                conditions += 1
                condition = approved
        event_id = f"{row['run_id']}:{name}:{sequences[name]}" if changed else None
        response = actual.get("response") or {}
        if (actual.get("type") != "request" or actual.get("step") != row["step"]
                or actual.get("status") != 200 or response.get("changed") is not changed
                or response.get("sequence") != sequences[name]
                or response.get("event_id") != event_id
                or response.get("duplicate_request") is not False):
            report["error"] = f"HTTP/causalidade divergente no passo {row['step']}"
            return report
    expected = calculate_expected_effects(rows)
    report["expected_effects"] = len(expected)
    source, logic, executor = (states.get(k) or {} for k in (
        "attribute-source", "logic-engine", "rule-executor"))
    checks = {
        "summary": summary.get("status") == "PASS"
                   and summary.get("requests_sent") == len(rows)
                   and type(summary.get("elapsed_ns")) is int,
        "source_values": source.get("attributes") == values,
        "source_sequences": source.get("sequences") == sequences,
        "logic_values": logic.get("attributes") == values,
        "logic_sequences": logic.get("sequences") == sequences,
        "condition_sequence": logic.get("condition_sequence") == conditions
                              and executor.get("condition_sequence") == conditions,
        "condition_state": logic.get("condition") is condition
                           and executor.get("approved") is condition,
        "effects": executor.get("effects") == expected,
        "ledger_counts": len(logic.get("received_ids") or []) == sum(sequences.values())
                         and len(executor.get("received_ids") or []) == conditions,
        "ready_without_fault": all(states.get(k, {}).get("ready") is True
                                   for k in states)
                               and not logic.get("faulted") and not executor.get("faulted")
                               and source.get("pending_request_id") is None,
    }
    report["checks"] = checks
    report["status"] = "PASS" if all(checks.values()) else "FAIL"
    return report


def archive(output):
    """Gera checksums sem auto-referencia; ZIP imutavel, sem remover originais."""
    output = Path(output)
    paths = sorted(p for p in output.iterdir() if p.is_file()
                   and p.name != "checksums.sha256")
    (output / "checksums.sha256").write_text(
        "".join(f"{hash_file(p)}  {p.name}\n" for p in paths),
        encoding="utf-8")
    zippath = output.with_suffix(".zip")
    if zippath.exists():
        raise FileExistsError(zippath)
    with ZipFile(zippath, "w", ZIP_DEFLATED) as zf:
        for p in sorted(output.iterdir()):
            if p.is_file():
                zf.write(p, p.name)
    return {"zip": str(zippath), "bytes": zippath.stat().st_size,
            "sha256": hash_file(zippath),
            "timestamp_utc": datetime.now(timezone.utc).isoformat()}
