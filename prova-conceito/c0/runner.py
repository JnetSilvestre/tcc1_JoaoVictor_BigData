"""CLI do cenário C0. Gera evidências reais e falha se divergirem."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

from .io import read_jsonl, validate_input, write_jsonl
from .oracle import calculate_expected_effects
from .pon_execution import execute_pon

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_sha():
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT,
            capture_output=True, text=True, check=False
        )
        return completed.stdout.strip() if completed.returncode == 0 else None
    except OSError:
        return None


def write_json(path, payload):
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def compare_effects(rows, manual_expected):
    expected_from_oracle = calculate_expected_effects(rows)
    execution = execute_pon(rows)
    actual = execution["effects"]
    report = {
        "scenario": "C0",
        "run_id": rows[0]["run_id"],
        "expected_fixture_matches_independent_oracle": manual_expected == expected_from_oracle,
        "pon_matches_manual_expected": actual == manual_expected,
        "pon_matches_independent_oracle": actual == expected_from_oracle,
        "expected_steps": [row["step"] for row in manual_expected],
        "observed_steps": [row["step"] for row in actual],
        "expected_count": len(manual_expected),
        "observed_count": len(actual),
        "trace_counts": dict(Counter(row["event_type"] for row in execution["trace"])),
        "final_state": execution["final_state"],
        "attribute_sequences": execution["attribute_sequences"],
        "condition_sequence": execution["condition_sequence"],
    }
    report["status"] = (
        "PASS" if all([
            report["expected_fixture_matches_independent_oracle"],
            report["pon_matches_manual_expected"],
            report["pon_matches_independent_oracle"],
        ]) else "FAIL"
    )
    return report, execution, expected_from_oracle


def main(argv=None):
    parser = argparse.ArgumentParser(description="TCC2 - C0 local verificável")
    parser.add_argument(
        "--input", type=Path,
        default=PROJECT_ROOT / "fixtures" / "c0_minimo.jsonl"
    )
    parser.add_argument(
        "--expected", type=Path,
        default=PROJECT_ROOT / "fixtures" / "c0_esperado.jsonl"
    )
    parser.add_argument(
        "--output", type=Path,
        default=PROJECT_ROOT / "resultados-locais" / "c0-minimo"
    )
    args = parser.parse_args(argv)

    try:
        rows = read_jsonl(args.input)
        run_id, seed = validate_input(rows)
        expected = read_jsonl(args.expected)
    except (OSError, ValueError) as exc:
        print(f"INVALID_INPUT: {exc}", file=sys.stderr)
        return 2

    report, execution, computed_oracle = compare_effects(rows, expected)

    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "scenario": "C0",
        "run_id": run_id,
        "seed": seed,
        "snapshot_version": f"{run_id}:snapshot:0",
        "initial_state": {"atA": 0, "atB": 0},
        "input_file": str(args.input.resolve()),
        "input_sha256": sha256_file(args.input),
        "expected_file": str(args.expected.resolve()),
        "expected_sha256": sha256_file(args.expected),
        "execution_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "git_sha": git_sha(),
        "note": "C0 processo unico, sem Docker/Kubernetes; sem métricas de desempenho",
    }
    write_jsonl(args.output / "effects.jsonl", execution["effects"])
    write_jsonl(args.output / "trace.jsonl", execution["trace"])
    write_jsonl(args.output / "oracle_independente.jsonl", computed_oracle)
    write_json(args.output / "validation.json", report)
    write_json(args.output / "manifest.json", manifest)
    files = [
        "effects.jsonl", "trace.jsonl", "oracle_independente.jsonl",
        "validation.json", "manifest.json",
    ]
    checksums = [
        f"{sha256_file(args.output / filename)}  {filename}"
        for filename in files
    ]
    (args.output / "checksums.sha256").write_text(
        "\n".join(checksums) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Artefatos: {args.output.resolve()}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
