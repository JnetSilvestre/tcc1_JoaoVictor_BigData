"""Testes de C0 e do oráculo independente (somente biblioteca padrão)."""

from collections import Counter
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from c0.io import read_jsonl, validate_input
from c0.oracle import calculate_expected_effects
from c0.pon_execution import execute_pon
from c0.runner import compare_effects


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "fixtures" / "c0_minimo.jsonl"
EXPECTED = ROOT / "fixtures" / "c0_esperado.jsonl"


class C0ScenarioTests(unittest.TestCase):

    def setUp(self):
        self.rows = read_jsonl(INPUT)
        self.expected = read_jsonl(EXPECTED)
        validate_input(self.rows)

    def test_independent_oracle_agrees_with_manually_versioned_fixture(self):
        self.assertEqual(calculate_expected_effects(self.rows), self.expected)
        self.assertEqual([row["step"] for row in self.expected], [3, 7])

    def test_pon_matches_expected_sequence_and_causality(self):
        report, execution, oracle = compare_effects(self.rows, self.expected)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(execution["effects"], self.expected)
        self.assertEqual(oracle, self.expected)
        self.assertEqual(report["final_state"], {
            "atA": 6, "atB": 1, "condition": True
        })

    def test_noop_and_transition_counts_are_exact(self):
        execution = execute_pon(self.rows)
        counts = Counter(event["event_type"] for event in execution["trace"])
        self.assertEqual(counts["request"], 7)
        self.assertEqual(counts["attribute_changed"], 5)
        self.assertEqual(counts["condition_changed"], 3)
        self.assertEqual(counts["rule_effect"], 2)
        self.assertEqual(execution["attribute_sequences"], {
            "atA": 2, "atB": 3
        })

    def test_replay_is_deterministic_for_logical_outputs(self):
        first = execute_pon(self.rows)
        second = execute_pon(self.rows)
        self.assertEqual(first, second)

    def test_invalid_request_or_value_is_rejected(self):
        duplicate = copy.deepcopy(self.rows)
        duplicate[1]["request_id"] = duplicate[0]["request_id"]
        with self.assertRaisesRegex(ValueError, "duplicado"):
            validate_input(duplicate)
        wrong_type = copy.deepcopy(self.rows)
        wrong_type[2]["value"] = True
        with self.assertRaisesRegex(ValueError, "inteiro"):
            validate_input(wrong_type)

    def test_cli_writes_real_trace_and_checksums(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "outputs"
            proc = subprocess.run([
                sys.executable, "-m", "c0.runner",
                "--input", str(INPUT), "--expected", str(EXPECTED),
                "--output", str(output),
            ], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            result = json.loads((output / "validation.json").read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(read_jsonl(output / "effects.jsonl"), self.expected)
            self.assertTrue((output / "checksums.sha256").exists())
            self.assertEqual(len((output / "checksums.sha256").read_text(encoding="utf-8").splitlines()), 5)

    def test_cli_fails_if_manual_expected_is_corrupted(self):
        wrong = copy.deepcopy(self.expected)
        wrong[0]["step"] = 999
        with tempfile.TemporaryDirectory() as tmp:
            wrong_file = Path(tmp) / "wrong.jsonl"
            wrong_file.write_text(
                "\n".join(json.dumps(x) for x in wrong) + "\n", encoding="utf-8"
            )
            output = Path(tmp) / "outputs"
            proc = subprocess.run([
                sys.executable, "-m", "c0.runner",
                "--input", str(INPUT), "--expected", str(wrong_file),
                "--output", str(output),
            ], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
            result = json.loads((output / "validation.json").read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "FAIL")
            self.assertFalse(result["pon_matches_manual_expected"])


if __name__ == "__main__":
    unittest.main()
