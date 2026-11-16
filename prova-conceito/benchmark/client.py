"""Cliente HTTP serial em UM processo. MUTANTE: usar apenas em bancada E11 isolada.

Entrada: stdin JSONL de fixture rebased. Saida: JSONL de respostas + summary.
O servico atual usa HTTP/1.0: nao presumir conexao TCP keep-alive.
A escrita das respostas em stdout ocorre apos fechar a janela medida.
"""
import argparse
from datetime import datetime, timezone
import http.client
import json
import sys
import time
from urllib.parse import urlsplit


def execute(rows, base_url, timeout):
    target = urlsplit(base_url)
    if target.scheme != "http" or not target.hostname or target.username or target.password:
        raise ValueError("URL HTTP sem credenciais obrigatoria")
    if target.path not in ("", "/") or target.query or target.fragment:
        raise ValueError("URL deve apontar somente ao host/porta")
    connection = http.client.HTTPConnection(target.hostname, target.port or 80, timeout=timeout)
    records = []
    batch_started_utc = datetime.now(timezone.utc).isoformat()
    begin = time.perf_counter_ns()
    failure = None
    try:
        for row in rows:
            if not isinstance(row, dict) or not {"run_id", "request_id", "entity_id", "value", "step"}.issubset(row):
                raise ValueError("linha de fixture invalida")
            payload = {k: row[k] for k in ("run_id", "request_id", "entity_id", "value", "step")}
            body = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")
            t0 = time.perf_counter_ns()
            try:
                connection.request("POST", "/attributes/change", body=body,
                                   headers={"Content-Type": "application/json"})
                response = connection.getresponse()
                status = response.status
                decoded = json.loads(response.read().decode("utf-8"))
            except Exception as exc:
                records.append({"type": "request", "step": row["step"],
                                "duration_ns": time.perf_counter_ns()-t0,
                                "status": None, "response": None,
                                "error": f"{type(exc).__name__}: {exc}"})
                failure = "falha de transporte; sem retry automatico"
                break
            records.append({"type": "request", "step": row["step"],
                            "duration_ns": time.perf_counter_ns()-t0,
                            "status": status, "response": decoded})
            if status != 200:
                failure = f"HTTP inesperado no passo {row['step']}: {status}"
                break
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        elapsed = time.perf_counter_ns() - begin
        batch_finished_utc = datetime.now(timezone.utc).isoformat()
        connection.close()
    summary = {"type": "summary", "status": "PASS" if failure is None
               and len(records) == len(rows) else "FAIL",
               "error": failure, "requests_target": len(rows),
               "requests_sent": len(records), "elapsed_ns": elapsed,
               "clock": "time.perf_counter_ns",
               "batch_started_utc": batch_started_utc,
               "batch_finished_utc": batch_finished_utc,
               "time_alignment_note": "UTC marks approximate boundaries only; no cross-clock latency",
               "end_utc": batch_finished_utc}
    return records, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 120:
        parser.error("timeout deve estar em (0,120] segundos")
    try:
        rows = [json.loads(line) for line in sys.stdin if line.strip()]
        if not rows:
            raise ValueError("fixture vazia")
        records, summary = execute(rows, args.url, args.timeout)
    except Exception as exc:
        records, summary = [], {"type": "summary", "status": "FAIL",
                                "error": f"{type(exc).__name__}: {exc}",
                                "requests_target": None, "requests_sent": 0,
                                "elapsed_ns": None}
    for record in records:
        print(json.dumps(record, separators=(",", ":"), ensure_ascii=True))
    print(json.dumps(summary, separators=(",", ":"), ensure_ascii=True))
    return 0 if summary["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
