"""Um papel C1 por processo, com HTTP/JSON serial em loopback."""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

from .client import ResponseError, request
from .protocol import ContractError, utc_now
from .state import AttributeSource, LogicEngine, RuleExecutor

ROLES = ("attribute-source", "logic-engine", "rule-executor")
MAX_BODY = 65536


def build_role(role, downstream, emit):
    def forward(path):
        def send(payload):
            emit("send", path=path, payload=payload)
            try:
                result = request(downstream, path, payload)
            except (OSError, ResponseError, ValueError) as error:
                raise ContractError(f"falha downstream: {error}", status=502) from error
            if result.get("ready") is False:
                raise ContractError("downstream indisponivel", status=502)
            emit("ack", path=path, payload=payload, response=result)
        return send

    if role == "attribute-source":
        state = AttributeSource(forward("/init/snapshot"), forward("/notifications/attribute"))

        def initialize(payload):
            if not isinstance(payload, dict) or set(payload) != {"run_id"}:
                raise ContractError("esperado objeto com run_id")
            return state.initialize(payload["run_id"])

        return state, {"/init/snapshot": initialize, "/attributes/change": state.change}
    if role == "logic-engine":
        state = LogicEngine(forward("/init/snapshot"), forward("/notifications/condition"))
        return state, {"/init/snapshot": state.initialize, "/notifications/attribute": state.receive}
    state = RuleExecutor()
    return state, {"/init/snapshot": state.initialize, "/notifications/condition": state.receive}


def serve(role, port, downstream):
    identity = {"service": role, "pid": os.getpid()}

    def emit(event_type, **fields):
        print(json.dumps({
            **identity, "timestamp": utc_now(), "event_type": event_type, **fields,
        }, ensure_ascii=True), flush=True)

    state, mutations = build_role(role, downstream, emit)

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            self.request.settimeout(10)
            super().setup()

        def log_message(self, *args):
            pass

        def respond(self, status, body):
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health/live":
                self.respond(200, {**identity, "live": True})
            elif self.path == "/health/ready":
                self.respond(200 if state.ready else 503, {**identity, "ready": state.ready})
            elif self.path == "/state":
                self.respond(200, {**identity, **state.state()})
            else:
                self.respond(404, {"error": "rota desconhecida"})

        def read_payload(self):
            if self.headers.get_content_type() != "application/json":
                raise ContractError("esperado application/json", status=415)
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError as error:
                raise ContractError("Content-Length invalido", status=400) from error
            if not 0 < length <= MAX_BODY:
                raise ContractError("tamanho de corpo invalido", status=413)
            try:
                return json.loads(self.rfile.read(length).decode("utf-8"))
            except (ValueError, RecursionError) as error:
                raise ContractError("JSON invalido", status=400) from error

        def do_POST(self):
            operation = mutations.get(self.path)
            if operation is None:
                self.respond(404, {"error": "rota desconhecida"})
                return
            payload = None
            try:
                payload = self.read_payload()
                previous_effects = len(state.effects) if isinstance(state, RuleExecutor) else 0
                result = operation(payload)
                status = 200
                if isinstance(state, RuleExecutor):
                    for effect in state.effects[previous_effects:]:
                        emit("effect", payload=effect)
            except ContractError as error:
                status, result = error.status, {"error": str(error)}
            emit("mutation", path=self.path, payload=payload, status=status, response=result)
            self.respond(status, result)

    with HTTPServer(("127.0.0.1", port), Handler) as server:
        emit("listening", port=server.server_port)
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=ROLES)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--downstream-port", type=int)
    args = parser.parse_args()
    if args.role != "rule-executor" and not 1 <= (args.downstream_port or 0) <= 65535:
        parser.error("informe --downstream-port para este papel")
    serve(args.role, args.port, args.downstream_port)


if __name__ == "__main__":
    main()
