"""E11-M00I: checks puros/mocks, nenhum Docker/Kubernetes e nenhum POST."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from benchmark.m01_readiness import (
    ARCHIVES, FIXTURE_SHA, ORDER, check_completed_sacrificial_archives,
    full_schedule, inspect_global_exclusivity, prepare_readonly_report,
)

GIT_SHA = "a" * 40


def fake_reader(*argv, docker_extra="", network_extra="", ns_extra=None,
                dirty=False):
    if argv == ("git", "branch", "--show-current"):
        return "tcc2/desenvolvimento"
    if argv == ("git", "status", "--porcelain"):
        return "dirty" if dirty else ""
    if argv == ("git", "rev-parse", "HEAD"):
        return GIT_SHA
    if argv == ("docker", "ps", "-a", "--format", "{{.Names}}"):
        return "tcc2-v05-attribute-source\n" + docker_extra
    if argv == ("docker", "network", "ls", "--format", "{{.Name}}"):
        return "bridge\nkind\ntcc2-pon-c2-v06\n" + network_extra
    if argv == ("kubectl", "--context", "kind-tcc2-pon",
                "get", "namespaces", "-o", "json"):
        names = ["default", "tcc2-pon", "tcc2-pon-c4"]
        if ns_extra is not None:
            names += ns_extra
        return json.dumps({
            "items": [{"metadata": {"name": x, "uid": x+"-uid"}} for x in names]
        })
    raise AssertionError(f"comando inesperado: {argv!r}")


def approved_host(*args):
    return {
        "node_allocatable": {
            "tcc2-pon-worker": {"uid": "w", "ready": True},
            "tcc2-pon-control-plane": {"uid": "c", "ready": True},
        },
    }


class ReadinessTests(unittest.TestCase):
    def test_schedule_has_exact_original_order_and_30_unique_ids(self):
        rows = full_schedule()
        self.assertEqual(len(rows), 30)
        self.assertEqual(len({x["run_id"] for x in rows}), 30)
        self.assertEqual([(x["block"], x["scenario"])
                          for x in rows[:3]],
                         [("B01", "C2"), ("B01", "C3"), ("B01", "C4")])
        self.assertEqual([x["scenario"] for x in rows[3:6]],
                         ["C3", "C4", "C2"])
        self.assertEqual([x["scenario"] for x in rows[-3:]],
                         ["C4", "C3", "C2"])
        self.assertEqual([x["scenario"] for x in rows],
                         [role for block in ORDER for role in block])
        self.assertEqual({x["requests"] for x in rows}, {1000})
        self.assertEqual({x["measurement_mode"] for x in rows}, {"timing_only"})

    def test_schedule_each_scenario_has_ten_runs(self):
        rows = full_schedule()
        for role in ("C2", "C3", "C4"):
            self.assertEqual(sum(x["scenario"] == role for x in rows), 10)
        self.assertEqual(rows[0]["run_id"], "e11-c2-m01-b01")
        self.assertEqual(rows[-1]["run_id"], "e11-c2-m01-b10")

    def test_exclusivity_allows_old_names_and_no_new(self):
        status = inspect_global_exclusivity(fake_reader)
        self.assertEqual(status["status"], "NO_NEW_M01_RESOURCES_PRESENT")

    def test_exclusivity_blocks_stopped_docker_m01(self):
        def query(*argv):
            return fake_reader(*argv,
                docker_extra="tcc2-pon-e11-c2-m01-b01-logic-engine")
        with self.assertRaisesRegex(ValueError, "ainda existe"):
            inspect_global_exclusivity(query)

    def test_exclusivity_blocks_orphan_m01_network(self):
        def query(*argv):
            return fake_reader(*argv,
                network_extra="tcc2-pon-e11-c2-m01-b02")
        with self.assertRaisesRegex(ValueError, "ainda existe"):
            inspect_global_exclusivity(query)

    def test_exclusivity_blocks_old_m01_kube_namespace(self):
        def query(*argv):
            return fake_reader(*argv,
                ns_extra=["tcc2-pon-e11-c4-m01-b01"])
        with self.assertRaisesRegex(ValueError, "ainda existe"):
            inspect_global_exclusivity(query)

    def test_missing_historic_namespaces_blocks(self):
        def query(*argv):
            if argv[0] == "kubectl":
                return json.dumps({"items":[{"metadata":{"name":"default"}}]})
            return fake_reader(*argv)
        with self.assertRaisesRegex(ValueError, "historicos"):
            inspect_global_exclusivity(query)

    def test_readonly_report_never_authorizes_execution(self):
        with patch("benchmark.m01_readiness.sha256_file",
                   return_value=FIXTURE_SHA), patch(
                   "benchmark.m01_readiness.check_completed_sacrificial_archives",
                   return_value={"C2": {}, "C3": {}, "C4": {}}), patch(
                   "benchmark.m01_readiness.assess_capacity",
                   return_value={"status": "CAPACITY_SAFETY_GATE_PASS_NOT_PERFORMANCE_APPROVAL",
                                 "windows_free_bytes": 5*1024**3,
                                 "disk_free_bytes": 30*1024**3}):
            result = prepare_readonly_report(
                "home", "backup", "inputs.jsonl", fake_reader, approved_host)
        self.assertEqual(result["matrix_size"], 30)
        self.assertEqual(result["status"],
                         "M01_READONLY_BASELINE_PASS_NOT_EXECUTION_AUTHORIZATION")
        self.assertFalse(result["start_authorized"])
        self.assertFalse(result["generalized_retirement_lifecycle_approved"])
        self.assertEqual(result["mutation_commands"], [])
        self.assertFalse(result["main_b01_started"])

    def test_changed_fixture_blocks_report(self):
        with patch("benchmark.m01_readiness.sha256_file",
                   return_value="0"*64):
            with self.assertRaisesRegex(ValueError, "fixture"):
                prepare_readonly_report(
                    "home", "backup", "inputs.jsonl", fake_reader, approved_host)

    def test_dirty_git_blocks_before_checks(self):
        def dirty_reader(*argv):
            return fake_reader(*argv, dirty=True)
        with self.assertRaisesRegex(ValueError, "modificada"):
            prepare_readonly_report(
                "home", "backup", "inputs.jsonl", dirty_reader, approved_host)

    def test_journals_require_real_completed_status(self):
        with TemporaryDirectory() as temp:
            home, backup_root = Path(temp)/"home", Path(temp)/"backups"
            for scenario, item in ARCHIVES.items():
                parent = backup_root/item["event"]
                parent.mkdir(parents=True)
                (parent/item["journal"]).write_text(json.dumps({
                    "stage":"COMPLETE",
                    "status": item["last_status"],
                    "run_id": f"e11-{scenario.lower()}-m01-s01",
                })+"\n", encoding="utf-8")
            with patch("benchmark.m01_readiness.sha256_file",
                       return_value=next(iter(ARCHIVES.values()))["sha"]), patch(
                       "benchmark.m01_readiness.audit_archive",
                       return_value={}), patch(
                       "benchmark.m01_readiness.compare_backup_pair",
                       return_value={}):
                with self.assertRaisesRegex(ValueError, "ZIP de|ZIP ou backup"):
                    check_completed_sacrificial_archives(home, backup_root)
            (backup_root/"E11-M00H"/ARCHIVES["C4"]["journal"]).write_text(
                '{"stage":"INTERRUPTED_DO_NOT_RETRY"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "journal C4 nao comprova"):
                # Os dois primeiros cenarios mockados retornam PASS.
                def hash_by_file(path):
                    for scenario, item in ARCHIVES.items():
                        if item["event"] in str(path):
                            return item["sha"]
                    return "0"*64
                def audited(primary, scenario, label, run_id):
                    return {
                        "status": "ZIP_INTEGRITY_VERIFIED_NOT_DELETION_AUTHORIZATION",
                        "zip_sha256": ARCHIVES[scenario]["sha"],
                    }
                def copied(primary, backup):
                    for item in ARCHIVES.values():
                        if item["event"] in str(primary):
                            return {
                                "status": "BACKUP_BYTES_VERIFIED_NO_CLEANUP_AUTHORIZATION",
                                "zip_sha256": item["sha"],
                                "different_filesystem_volume": True,
                                "delete_authorized": False,
                            }
                with patch("benchmark.m01_readiness.sha256_file",
                           side_effect=hash_by_file), patch(
                           "benchmark.m01_readiness.audit_archive",
                           side_effect=audited), patch(
                           "benchmark.m01_readiness.compare_backup_pair",
                           side_effect=copied):
                    check_completed_sacrificial_archives(home, backup_root)


if __name__ == "__main__":
    unittest.main()
