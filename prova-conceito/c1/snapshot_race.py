"""Ensaio C1 de uma alteração HTTP recebida durante o handshake do snapshot.

Três processos reais (source/logic/executor) + um proxy de teste em thread,
usado SOMENTE para atrasar a confirmação do snapshot. Os serviços produtivos
não têm hooks de teste, e cada servidor da prova permanece HTTP serial.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from datetime import datetime, timezone
from http.client import HTTPResponse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import platform
import socket
import subprocess
import sys
from threading import Event, Thread
import time

from c0.io import read_jsonl, validate_input, write_jsonl
from c0.runner import PROJECT_ROOT, git_sha, sha256_file, write_json
from .client import request
from .runner import stop
from .service import ROLES


def _utc():
    return datetime.now(timezone.utc).isoformat()


def _start(role, downstream, output, stack):
    stdout = stack.enter_context((output / f"{role}.jsonl").open("wb"))
    stderr = stack.enter_context((output / f"{role}.stderr.log").open("wb"))
    command = [sys.executable, "-m", "c1.service", role]
    if downstream is not None:
        command += ["--downstream-port", str(downstream)]
    proc = subprocess.Popen(command, cwd=PROJECT_ROOT, stdout=stdout, stderr=stderr)
    stack.callback(stop, proc)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        first, separator, _ = (output / f"{role}.jsonl").read_bytes().partition(b"\n")
        if separator:
            startup = json.loads(first)
            if startup.get("service") != role or startup.get("pid") != proc.pid:
                raise RuntimeError(f"Identidade inesperada de {role}: {startup}")
            return startup["port"], proc.pid
        if proc.poll() is not None:
            raise RuntimeError(f"Processo {role} terminou antes de anunciar porta: {proc.returncode}")
        time.sleep(0.05)
    raise TimeoutError(f"Processo {role} não anunciou porta")


def _raw_post(port, path, payload):
    """Envia a requisição COMPLETA no socket antes de liberar o ACK."""
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    message = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(data)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode("ascii") + data
    sock = socket.create_connection(("127.0.0.1", port), timeout=5)
    sock.settimeout(8)
    try:
        sock.sendall(message)
    except Exception:
        sock.close()
        raise
    return sock


def _read_response(sock):
    try:
        response = HTTPResponse(sock)
        response.begin()
        status = response.status
        payload = json.loads(response.read().decode("utf-8"))
        return status, payload
    finally:
        sock.close()


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    rows = read_jsonl(PROJECT_ROOT / "fixtures" / "c0_minimo.jsonl")
    run_id, seed = validate_input(rows)
    expected = read_jsonl(PROJECT_ROOT / "fixtures" / "c0_esperado.jsonl")
    # O passo 1 escreve atA=0 (nenhuma mudança). O passo 2 é a alteração
    # efetiva injetada durante o handshake, seguida dos passos 3 a 7.
    changes = [{k: v for k, v in row.items() if k != "seed"} for row in rows]
    report = {"scenario": "C1-snapshot-http-race", "run_id": run_id, "status": "FAIL"}
    timeline = []
    manifest = {
        "scenario": "C1-snapshot-http-race", "run_id": run_id, "seed": seed,
        "git_sha": git_sha(), "python": platform.python_version(),
        "platform": platform.platform(), "timestamp": _utc(),
        "fixture_sha256": sha256_file(PROJECT_ROOT / "fixtures" / "c0_minimo.jsonl"),
        "expected_sha256": sha256_file(PROJECT_ROOT / "fixtures" / "c0_esperado.jsonl"),
        "test_transport": "HTTP loopback; 3 service PIDs; gated ACK proxy in test process",
        "limitation": "serial source HTTPServer, one controlled transition; no crash recovery",
    }

    def mark(event, **fields):
        timeline.append({
            "event": event, "monotonic_ns": time.monotonic_ns(),
            "utc": _utc(), **fields,
        })

    gate_release = Event()
    snapshot_forwarded = Event()

    try:
        with ExitStack() as stack:
            exec_port, exec_pid = _start("rule-executor", None, output, stack)
            logic_port, logic_pid = _start("logic-engine", exec_port, output, stack)

            class GateHandler(BaseHTTPRequestHandler):
                def log_message(self, *_):
                    pass

                def do_POST(self):
                    length = int(self.headers.get("Content-Length", "0"))
                    payload = json.loads(self.rfile.read(length))
                    if self.path not in ("/init/snapshot", "/notifications/attribute"):
                        self.send_error(404)
                        return
                    try:
                        result = request(logic_port, self.path, payload)
                    except Exception as exc:
                        mark("gate_downstream_error", error=str(exc))
                        self.send_error(502)
                        return
                    if self.path == "/init/snapshot":
                        mark("snapshot_installed_downstream")
                        snapshot_forwarded.set()
                        if not gate_release.wait(timeout=3):
                            self.send_error(504, "snapshot gate timeout")
                            return
                        mark("snapshot_ack_released")
                    else:
                        mark("attribute_forwarded", event_id=payload["event_id"])
                    body = json.dumps(result).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

            gate = HTTPServer(("127.0.0.1", 0), GateHandler)
            gate_thread = Thread(target=gate.serve_forever, daemon=True)
            gate_thread.start()

            def close_gate():
                gate_release.set()
                gate.shutdown()
                gate.server_close()
                gate_thread.join(timeout=5)

            stack.callback(close_gate)
            source_port, source_pid = _start("attribute-source", gate.server_port, output, stack)
            manifest["ports"] = {
                "attribute-source": source_port,
                "logic-engine": logic_port,
                "rule-executor": exec_port,
                "snapshot-gate-test": gate.server_port,
            }
            manifest["pids"] = {
                "attribute-source": source_pid,
                "logic-engine": logic_pid,
                "rule-executor": exec_pid,
            }
            checks = {"three_distinct_pids": len({source_pid, logic_pid, exec_pid}) == 3}
            if not checks["three_distinct_pids"]:
                raise RuntimeError("PIDs dos serviços não são distintos")

            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(request, source_port, "/init/snapshot", {"run_id": run_id})
                if not snapshot_forwarded.wait(timeout=4):
                    raise TimeoutError("Proxy não observou instalação do snapshot")
                mark("snapshot_ack_held")
                # O downstream já instalou o snapshot, mas o produtor
                # permanece bloqueado aguardando a confirmação.
                before_logic = request(logic_port, "/state")
                before_exec = request(exec_port, "/state")
                checks["downstream_initialized_no_effects"] = (
                    before_logic["ready"] and before_exec["ready"]
                    and before_logic["attributes"] == {"atA": 0, "atB": 0}
                    and before_logic["sequences"] == {"atA": 0, "atB": 0}
                    and before_exec["effects"] == []
                )
                # O socket envia o corpo completo enquanto a requisição de
                # snapshot ainda está presa no HTTPServer serial do produtor.
                pending_socket = _raw_post(source_port, "/attributes/change", changes[1])
                mark("concurrent_change_sent", request_id=changes[1]["request_id"])
                gate_release.set()
                init_ack = future.result(timeout=6)
                status, race_response = _read_response(pending_socket)
                mark("concurrent_change_responded", status=status)
                checks["change_completed_after_snapshot"] = (
                    init_ack.get("ready") is True
                    and status == 200 and race_response.get("changed") is True
                    and race_response.get("sequence") == 1
                    and race_response.get("event_id") == f"{run_id}:atA:1"
                )

            # A alteração concorrente foi o passo 2. Aplicamos 3 a 7,
            # inclusive o no-op do passo 4. A omissão do passo 1 é segura:
            # atA já inicia com zero, portanto não produz notificação.
            for change in changes[2:]:
                request(source_port, "/attributes/change", change)

            states = {
                role: request(port, "/state")
                for role, port in (
                    ("attribute-source", source_port),
                    ("logic-engine", logic_port),
                    ("rule-executor", exec_port),
                )
            }
            effects = states["rule-executor"]["effects"]
            checks["expected_effects_and_causality"] = effects == expected
            checks["final_consistent_state"] = (
                states["attribute-source"]["attributes"]
                == states["logic-engine"]["attributes"]
                == {"atA": 6, "atB": 1}
                and states["attribute-source"]["sequences"]
                == states["logic-engine"]["sequences"]
                == {"atA": 2, "atB": 3}
                and states["logic-engine"]["condition_sequence"]
                == states["rule-executor"]["condition_sequence"] == 3
            )
            checks["no_extra_events"] = (
                len(states["logic-engine"]["received_ids"]) == 5
                and len(states["rule-executor"]["received_ids"]) == 3
                and len(effects) == 2
            )
            seen = {entry["event"]: entry["monotonic_ns"] for entry in timeline}
            checks["ordered_gate_timeline"] = (
                seen["snapshot_installed_downstream"]
                <= seen["snapshot_ack_held"]
                <= seen["concurrent_change_sent"]
                <= seen["snapshot_ack_released"]
                <= seen["concurrent_change_responded"]
            )
            report.update({
                "checks": checks,
                "effects_steps": [effect["step"] for effect in effects],
                "status": "PASS" if all(checks.values()) else "FAIL",
            })
            write_json(output / "states.json", states)
            write_jsonl(output / "effects.jsonl", effects)
            write_jsonl(output / "expected.jsonl", expected)
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        gate_release.set()
        write_jsonl(output / "timeline.jsonl", timeline)
        write_json(output / "validation.json", report)
        write_json(output / "manifest.json", manifest)
        (output / "checksums.sha256").write_text(
            "".join(
                f"{sha256_file(path)}  {path.name}\n"
                for path in sorted(output.iterdir()) if path.name != "checksums.sha256"
            ),
            encoding="utf-8",
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = run(args.output)
    except OSError as exc:
        print(f"Falha de preparação: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
