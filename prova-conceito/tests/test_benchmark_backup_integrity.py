"""E11-M00: verificacao de copia ZIP, sem remoção ou operacoes em runtime."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from benchmark.backup_integrity import compare_backup_pair, sha256_file, verify_zip_bytes


def make_zip(path, value=b"synthetic"):
    with ZipFile(path, "w", ZIP_DEFLATED) as output:
        output.writestr("manifest.json", value)
        output.writestr(
            "checksums.sha256",
            hashlib.sha256(value).hexdigest() + "  manifest.json\n")


class BackupIntegrityTests(unittest.TestCase):
    def test_verified_same_volume_is_not_claimed_to_be_independent(self):
        with TemporaryDirectory() as home:
            root = Path(home)
            first, second = root / "a" / "run.zip", root / "b" / "copy.zip"
            first.parent.mkdir()
            second.parent.mkdir()
            make_zip(first)
            second.write_bytes(first.read_bytes())
            result = compare_backup_pair(first, second)
            self.assertEqual(result["status"],
                             "BACKUP_BYTES_VERIFIED_NO_CLEANUP_AUTHORIZATION")
            self.assertFalse(result["different_filesystem_volume"])
            self.assertFalse(result["delete_authorized"])
            self.assertEqual(result["commands"], [])
            self.assertEqual(result["zip_sha256"], sha256_file(first))

    def test_source_equals_backup_rejected(self):
        with TemporaryDirectory() as home:
            one = Path(home) / "run.zip"
            make_zip(one)
            with self.assertRaises(ValueError):
                compare_backup_pair(one, one)

    def test_mismatch_copy_blocks(self):
        with TemporaryDirectory() as home:
            root = Path(home)
            one, two = root / "a" / "a.zip", root / "b" / "b.zip"
            one.parent.mkdir()
            two.parent.mkdir()
            make_zip(one, b"abc")
            make_zip(two, b"xyz")
            with self.assertRaises(ValueError):
                compare_backup_pair(one, two)

    def test_corrupt_internal_checksum_rejected(self):
        with TemporaryDirectory() as home:
            one = Path(home) / "bad.zip"
            with ZipFile(one, "w") as output:
                output.writestr("manifest.json", "original")
                output.writestr("checksums.sha256", "0"*64+"  manifest.json\n")
            with self.assertRaises(ValueError):
                verify_zip_bytes(one)

    def test_missing_backup_rejected_without_writing(self):
        with TemporaryDirectory() as home:
            root = Path(home)
            one = root / "run.zip"
            make_zip(one)
            with self.assertRaises(ValueError):
                compare_backup_pair(one, root / "not-found.zip")


if __name__ == "__main__":
    unittest.main()
