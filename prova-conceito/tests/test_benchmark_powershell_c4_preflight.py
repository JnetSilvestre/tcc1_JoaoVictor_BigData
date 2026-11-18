"""E11-M00H: regressão de constantes congeladas do PowerShell C4."""
from pathlib import Path
import re
import unittest

from benchmark.ownership import IMAGE_ID

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "e11_m00h_qualificacao_c4.ps1"
INPUT_SHA256 = "26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551"


class C4PowerShellPreflightTests(unittest.TestCase):
    def test_c4_image_and_fixture_are_exactly_canonical(self):
        script = SCRIPT.read_text(encoding="utf-8")
        image = re.search(
            r'(?m)^\s*\$approvedImageID\s*=\s*"(sha256:[0-9a-f]{64})"\s*$',
            script,
        )
        fixture = re.search(
            r'(?m)^\s*\$approvedFixtureHash\s*=\s*"([0-9a-f]{64})"\s*$',
            script,
        )
        self.assertIsNotNone(image, "ID de imagem C4 ausente ou truncado")
        self.assertIsNotNone(fixture, "SHA de fixture C4 ausente ou truncado")
        self.assertEqual(image.group(1), IMAGE_ID)
        self.assertEqual(fixture.group(1), INPUT_SHA256)
        self.assertIn("IMAGE_ID_OBSERVADO:", script)
        self.assertIn("FIXTURE_SHA256_OBSERVADO:", script)
        self.assertIn("Ran 129 tests", script)
        self.assertIn("--scenario C4", script)
        self.assertIn("C3_S01_RETIREMENT_COMPLETE", script)


if __name__ == "__main__":
    unittest.main()
