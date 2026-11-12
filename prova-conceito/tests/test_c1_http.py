"""Integração HTTP real com três interpretadores Python independentes."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from c0.io import read_jsonl
from c0.runner import sha256_file
from c1.runner import run


class C1HTTPTests(unittest.TestCase):
    def test_fixture_and_protocol_over_loopback(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            report = run(output)
            self.assertEqual(report["status"], "PASS", report)
            self.assertEqual(report["steps"], [3, 7])
            self.assertEqual(len(read_jsonl(output / "effects.jsonl")), 2)
            self.assertEqual(
                read_jsonl(output / "effects.jsonl"), read_jsonl(output / "c0-effects.jsonl"),
            )
            checksums = (output / "checksums.sha256").read_text(encoding="utf-8")
            for entry in checksums.splitlines():
                digest, filename = entry.split("  ", 1)
                self.assertEqual(digest, sha256_file(output / filename), filename)
