"""E11-M00F: regressao estatica de SHA canonico no PowerShell."""
from pathlib import Path
import re
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "e11_m00f_preparacao_consolidada.ps1"
CANONICAL_INPUT_SHA256 = "26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551"


class PowerShellPreflightTests(unittest.TestCase):
    def test_fixture_constant_full_sha256_and_gate(self):
        script = SCRIPT.read_text(encoding="utf-8")
        pattern = r'(?m)^\s*\$expectedFixtureHash\s*=\s*"([0-9a-f]+)"\s*$'
        match = re.search(pattern, script)
        self.assertIsNotNone(match, "Constante de fixture nao localizada")
        self.assertEqual(len(match.group(1)), 64, "SHA-256 truncado")
        self.assertEqual(match.group(1), CANONICAL_INPUT_SHA256)
        self.assertIn('if ($fixtureHash -ne $expectedFixtureHash)', script)
        self.assertIn('throw "STOP: Fixture canonica divergente"', script)


if __name__ == "__main__":
    unittest.main()
