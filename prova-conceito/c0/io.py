"""Leitura/validação estrita de fixtures locais; nenhuma dependência extra."""

import json
from pathlib import Path


REQUIRED_INPUT_KEYS = {
    "run_id", "request_id", "entity_id", "value", "step", "seed"
}


def read_jsonl(path):
    path = Path(path)
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: JSON inválido") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: esperado objeto JSON")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path}: JSONL vazio")
    return rows


def validate_input(rows):
    if not rows:
        raise ValueError("Fixture sem entradas")
    first = rows[0]
    run_id = first.get("run_id")
    seed = first.get("seed")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id deve ser texto não vazio")
    if type(seed) is not int:
        raise ValueError("seed deve ser inteiro")
    requests = set()
    for step, row in enumerate(rows, start=1):
        if set(row) != REQUIRED_INPUT_KEYS:
            raise ValueError(f"passo {step}: campos incorretos")
        if type(row["step"]) is not int or row["step"] != step:
            raise ValueError(f"passo {step}: numeração não consecutiva")
        if row["run_id"] != run_id or row["seed"] != seed:
            raise ValueError(f"passo {step}: run_id/seed inconsistentes")
        if row["entity_id"] not in ("atA", "atB"):
            raise ValueError(f"passo {step}: entidade desconhecida")
        if type(row["value"]) is not int:
            raise ValueError(f"passo {step}: value deve ser inteiro, não booleano")
        req = row["request_id"]
        if not isinstance(req, str) or not req.strip() or req in requests:
            raise ValueError(f"passo {step}: request_id inválido/duplicado")
        requests.add(req)
    return run_id, seed


def write_jsonl(path, rows):
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            stream.write("\n")
