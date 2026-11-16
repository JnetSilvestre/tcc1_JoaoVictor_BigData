"""Geracao deterministica de carga: oito passos por ciclo, sem simular execucoes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random

from c0.io import validate_input, write_jsonl
from c0.oracle import calculate_expected_effects


DEFAULT_LOADS = ((100, 20260501), (1000, 20260502), (10000, 20260503))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def generate(count, seed, run_id):
    if type(count) is not int or not 1 <= count <= 100000:
        raise ValueError("quantidade fora de 1..100000")
    if type(seed) is not int or not isinstance(run_id, str) or not run_id:
        raise ValueError("seed/run_id invalidos")
    rng = random.Random(seed)
    rows = []
    for cycle in range((count + 7) // 8):
        # A ultima posicao retorna atB=0: dois disparos por ciclo completo.
        # A primeira posicao do primeiro ciclo e um no-op intencional.
        pattern = (
            ("atA", 0), ("atA", 5), ("atB", 1), ("atB", 1),
            ("atA", rng.randrange(7, 16)), ("atB", 0),
            ("atB", 1), ("atB", 0),
        )
        for entity, value in pattern:
            step = len(rows) + 1
            if step > count:
                break
            rows.append({
                "run_id": run_id, "request_id": f"req-{step:06d}",
                "entity_id": entity, "value": value,
                "step": step, "seed": seed,
            })
    validate_input(rows)
    return rows


def rebase(rows, run_id):
    rebased = [{**r, "run_id": run_id,
                "request_id": f"{run_id}:req:{r['step']}"} for r in rows]
    validate_input(rebased)
    return rebased


def characterize(rows):
    values = {"atA": 0, "atB": 0}
    changed = 0
    transitions = 0
    previous = False
    for row in rows:
        name, value = row["entity_id"], row["value"]
        if values[name] != value:
            changed += 1
            values[name] = value
            approved = values["atA"] >= 5 and values["atB"] == 1
            if approved != previous:
                transitions += 1
                previous = approved
    return {"requests": len(rows), "changed": changed,
            "unchanged": len(rows) - changed, "condition_transitions": transitions,
            "effects": len(calculate_expected_effects(rows)), "final_attributes": values,
            "entities": dict(Counter(r["entity_id"] for r in rows))}


def prepare(size, seed, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    run_id = f"e11-canonical-{size}-{seed}"
    rows = generate(size, seed, run_id)
    expected = calculate_expected_effects(rows)
    write_jsonl(output / "inputs.jsonl", rows)
    write_jsonl(output / "expected.jsonl", expected)
    meta = {"kind": "fixture_canonica_sem_execucao", "cycle_length": 8,
            "size": size, "seed": seed, "run_id": run_id,
            "counts": characterize(rows)}
    for name in ("inputs.jsonl", "expected.jsonl"):
        meta[name + "_sha256"] = sha256(output / name)
    (output / "metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return meta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sizes", nargs="+", type=int, default=[100, 1000, 10000])
    args = parser.parse_args()
    assignments = dict(DEFAULT_LOADS)
    if any(x not in assignments for x in args.sizes) or len(set(args.sizes)) != len(args.sizes):
        parser.error("sizes deve conter valores distintos de 100, 1000 e 10000")
    args.output.mkdir(parents=True, exist_ok=False)
    for size in args.sizes:
        meta = prepare(size, assignments[size], args.output / f"s{size}")
        print(json.dumps(meta, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
