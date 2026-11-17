"""E11-M00C: ZIP sintético e review-only; sem docker stop/rm/kubectl delete."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

from benchmark.lifecycle_audit import (
    MANDATORY, audit_archive, retirement_review_only, sha256_bytes,
)


def make_archive(path, scenario="C2", run_id="e11-c2-m01-b01",
                 fail=False, corrupt=False, missing=None):
    rows = {name: b"synthetic-test-only" for name in MANDATORY
            if name != "checksums.sha256"}
    rows["manifest.json"] = json.dumps({
        "scenario": scenario, "run_id": run_id,
        "measurement_mode": "timing_only",
    }).encode()
    rows["validation.json"] = json.dumps({
        "status": "FAIL" if fail else "PASS",
        "started_snapshot": True, "started_changes": True,
    }).encode()
    rows["environment.json"] = json.dumps({
        "scenario": scenario, "run_id": run_id,
    }).encode()
    rows["preflight-uniform.json"] = b'{"status":"PASS_COLD_READ_ONLY"}'
    rows["capacity-gate.json"] = json.dumps({
        "status": "CAPACITY_SAFETY_GATE_PASS_NOT_PERFORMANCE_APPROVAL"}).encode()
    rows["effective-quotas.json"] = json.dumps({
        "status": "EFFECTIVE_LIMITS_ALL_FOUR_PASS",
        "scenario": scenario,
        "roles": {role: {"status": "EFFECTIVE_CGROUP_LIMITS_PASS_NOT_USAGE_COMPARISON"}
                  for role in ("attribute-source", "logic-engine", "rule-executor", "client")},
    }).encode()
    if missing is not None:
        del rows[missing]
    sha_lines = "".join(f"{sha256_bytes(payload)}  {name}\n"
                        for name, payload in sorted(rows.items()))
    if corrupt:
        sha_lines = "0" * 64 + sha_lines[64:]
    rows["checksums.sha256"] = sha_lines.encode()
    with ZipFile(path, "w", ZIP_DEFLATED) as dest:
        for name, payload in rows.items():
            dest.writestr(name, payload)


class LifecycleAuditTests(unittest.TestCase):
    def test_integrity_pass_still_does_not_authorize_delete(self):
        with TemporaryDirectory() as temp:
            zip_path = Path(temp) / "evidence.zip"
            make_archive(zip_path)
            result = audit_archive(zip_path, "C2", "m01-b01", "e11-c2-m01-b01")
            self.assertTrue(result["functional_pass_verified"])
            self.assertFalse(result["delete_authorized"])
            review = retirement_review_only("C2", "m01-b01", "e11-c2-m01-b01", result)
            self.assertEqual(review["status"], "REVIEW_ONLY_NO_ACTION")
            self.assertEqual(review["commands"], [])
            self.assertFalse(review["delete_authorized"])
            self.assertNotIn("tcc2-v03", repr(review))

    def test_corrupt_hash_and_missing_artifact_block(self):
        with TemporaryDirectory() as temp:
            first, second = Path(temp) / "wrong.zip", Path(temp) / "missing.zip"
            make_archive(first, corrupt=True)
            make_archive(second, missing="environment.json")
            with self.assertRaises(ValueError):
                audit_archive(first, "C2", "m01-b01", "e11-c2-m01-b01")
            with self.assertRaises(ValueError):
                audit_archive(second, "C2", "m01-b01", "e11-c2-m01-b01")

    def test_failing_functional_run_cannot_be_retired(self):
        with TemporaryDirectory() as temp:
            zip_path = Path(temp) / "failed.zip"
            make_archive(zip_path, fail=True)
            with self.assertRaises(ValueError):
                audit_archive(zip_path, "C2", "m01-b01", "e11-c2-m01-b01")

    def test_missing_capacity_and_effective_quota_gates_block(self):
        for missing in ("capacity-gate.json", "effective-quotas.json"):
            with self.subTest(missing=missing), TemporaryDirectory() as temp:
                zip_path = Path(temp) / "incomplete.zip"
                make_archive(zip_path, missing=missing)
                with self.assertRaises(ValueError):
                    audit_archive(zip_path, "C2", "m01-b01", "e11-c2-m01-b01")

    def test_wrong_identity_historical_label_rejected(self):
        with TemporaryDirectory() as temp:
            zip_path = Path(temp) / "sample.zip"
            make_archive(zip_path)
            with self.assertRaises(ValueError):
                audit_archive(zip_path, "C2", "p20261115-232946",
                              "e11-c2-p20261115-232946")
            with self.assertRaises(ValueError):
                audit_archive(zip_path, "C4", "m01-b01", "e11-c4-m01-b01")

    def test_namespace_review_only_and_forbidden_untrusted_audit(self):
        with TemporaryDirectory() as temp:
            zip_path = Path(temp) / "sample.zip"
            make_archive(zip_path, scenario="C4", run_id="e11-c4-m01-b01")
            record = audit_archive(zip_path, "C4", "m01-b01", "e11-c4-m01-b01")
            result = retirement_review_only("C4", "m01-b01", "e11-c4-m01-b01", record)
            self.assertEqual(result["expected_new_resource_names"]["namespace"],
                             "tcc2-pon-e11-c4-m01-b01")
            self.assertFalse(result["delete_authorized"])
            with self.assertRaises(ValueError):
                retirement_review_only("C4", "m01-b01", "e11-c4-m01-b01",
                                       {"status": "APPROVED"})
            

if __name__ == "__main__":
    unittest.main()
