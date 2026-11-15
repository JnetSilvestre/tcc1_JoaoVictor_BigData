"""Testes sem Docker para a rodada consolidada V06 E08-D18G/H."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from c2.v06_batch import planned_cases, verify_hash_manifest


class V06BatchTests(unittest.TestCase):
    def test_only_two_pending_cases(self):
        cases = planned_cases()
        self.assertEqual([c[0] for c in cases], ["E08-D18G", "E08-D18H"])
        self.assertEqual([c[1] for c in cases], ["logic-engine", "rule-executor"])
        self.assertTrue(all(c[2].startswith("/notifications/") for c in cases))

    def test_run_id_mismatch_is_syntactically_valid(self):
        _, _, _, payload, expected = planned_cases()[0]
        self.assertEqual(payload["run_id"], "v06-other-run")
        self.assertEqual(payload["event_id"], "v06-other-run:atA:1")
        self.assertEqual(payload["sequence"], 1)
        self.assertEqual(expected, "run_id divergente")

    def test_condition_gap_is_syntactically_valid(self):
        _, _, _, payload, expected = planned_cases()[1]
        self.assertEqual(payload["run_id"], "v06-order-v1")
        self.assertEqual(payload["event_id"], "v06-order-v1:cn1:2")
        self.assertEqual(payload["sequence"], 2)
        self.assertTrue(payload["approved"])
        self.assertEqual(expected, "evento atrasado ou lacuna de sequence")

    def test_prior_hash_manifest_accepts_matching_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "data.json").write_text('{"ok":true}', encoding="utf-8")
            digest = hashlib.sha256((folder / "data.json").read_bytes()).hexdigest()
            (folder / "checksums.sha256").write_text(
                f"{digest}  data.json\n", encoding="utf-8")
            self.assertEqual(
                verify_hash_manifest(folder, 1), {"data.json": digest})

    def test_prior_hash_manifest_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "data.json").write_text("original", encoding="utf-8")
            digest = hashlib.sha256((folder / "data.json").read_bytes()).hexdigest()
            (folder / "checksums.sha256").write_text(
                f"{digest}  data.json\n", encoding="utf-8")
            (folder / "data.json").write_text("alterado", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash anterior divergente"):
                verify_hash_manifest(folder, 1)


if __name__ == "__main__":
    unittest.main()
