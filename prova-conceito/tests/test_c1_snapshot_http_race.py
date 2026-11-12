"""Ensaio HTTP real: alteração enfileirada enquanto snapshot aguarda ACK."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from c0.io import read_jsonl
from c0.runner import sha256_file
from c1.snapshot_race import run


class SnapshotRaceHTTPTests(unittest.TestCase):
    def test_change_during_snapshot_ack_over_http(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot-race"
            report = run(path)
            self.assertEqual(report["status"], "PASS", report)
            self.assertTrue(all(report["checks"].values()), report)
            self.assertEqual(report["effects_steps"], [3, 7])
            self.assertEqual(
                read_jsonl(path / "effects.jsonl"),
                read_jsonl(path / "expected.jsonl"),
            )
            timeline = read_jsonl(path / "timeline.jsonl")
            event_types = [entry["event"] for entry in timeline]
            self.assertIn("concurrent_change_sent", event_types)
            self.assertIn("snapshot_ack_released", event_types)
            self.assertLess(
                event_types.index("concurrent_change_sent"),
                event_types.index("snapshot_ack_released"),
            )
            manifest = json.loads(
                (path / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(set(manifest["pids"].values())), 3)
            for line in (path / "checksums.sha256").read_text(
                encoding="utf-8"
            ).splitlines():
                digest, filename = line.split("  ", 1)
                self.assertEqual(digest, sha256_file(path / filename))


if __name__ == "__main__":
    unittest.main()
