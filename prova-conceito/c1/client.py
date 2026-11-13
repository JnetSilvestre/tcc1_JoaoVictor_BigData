"""Cliente HTTP/JSON: loopback em C1, hostname de rede interna em C2."""

import json
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener


class ResponseError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


def request(port, path, payload=None, host="127.0.0.1"):
    data = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
    message = Request(
        f"http://{host}:{port}{path}", data=data,
        headers={"Content-Type": "application/json"},
    )
    opener = build_opener(ProxyHandler({}))
    try:
        with opener.open(message, timeout=5) as response:
            return json.load(response)
    except HTTPError as error:
        with error:
            raise ResponseError(error.code, json.load(error)) from error
