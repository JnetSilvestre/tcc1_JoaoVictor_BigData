"""E11-M00J: ensaios sintéticos do controlador de 30 slots (sem Docker real)."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from benchmark import m01_lifecycle as life


SHA = "a" * 40
HASH = "b" * 64


def empty_inventory(*args):
    if args == ("docker", "ps", "-a", "--format", "{{.Names}}"):
        return "tcc2-v05-attribute-source\n"
    if args == ("docker", "network", "ls", "--format", "{{.Name}}"):
        return "bridge\nkind\n"
    if args == ("kubectl", "--context", "kind-tcc2-pon",
                "get", "namespaces", "-o", "json"):
        return json.dumps({"items": [
            {"metadata": {"name": "default", "uid": "old-default"}},
            {"metadata": {"name": "tcc2-pon", "uid": "old-c3"}},
            {"metadata": {"name": "tcc2-pon-c4", "uid": "old-c4"}},
        ]})
    if args == ("git", "branch", "--show-current"):
        return "tcc2/desenvolvimento"
    if args == ("git", "status", "--porcelain"):
        return ""
    if args == ("git", "rev-parse", "HEAD"):
        return SHA
    raise AssertionError(f"consulta externa imprevista: {args!r}")


def approved_capacity(_scenario, _run_id):
    return {"status": "BASELINE_READ_ONLY_NOT_CAPACITY_APPROVAL",
            "docker_cgroup_version": "2",
            "windows_host_ram_free_bytes": 5 * 1024**3,
            "disk_free_bytes": 30 * 1024**3,
            "node_allocatable": {"tcc2-pon-worker": {"ready": True},
                                 "tcc2-pon-control-plane": {"ready": True}}}


def valid_audit(*args):
    return {"status": "ZIP_INTEGRITY_VERIFIED_NOT_DELETION_AUTHORIZATION",
            "zip_sha256": HASH, "delete_authorized": False}


def valid_backup(*args):
    return {"status": "BACKUP_BYTES_VERIFIED_NO_CLEANUP_AUTHORIZATION",
            "zip_sha256": HASH,
            "different_filesystem_volume": True,
            "delete_authorized": False, "commands": []}


def pod_inventory(ns):
    rows = []
    for kind, names in (
        ("Pod", ["as-pod", "le-pod", "re-pod", "e11-benchmark-client"]),
        ("Deployment", ["attribute-source", "logic-engine", "rule-executor"]),
        ("Service", ["attribute-source", "logic-engine", "rule-executor"]),
        ("ConfigMap", ["e11-c4-config", "kube-root-ca.crt"]),
        ("ServiceAccount", ["default"]),
    ):
        for name in names:
            rows.append({"kind": kind, "metadata": {"name": name, "namespace": ns}})
    for role in ("attribute-source", "logic-engine", "rule-executor"):
        rows.append({"kind": "ReplicaSet", "metadata": {
            "name": role + "-abc", "namespace": ns,
            "labels": {"app": role},
            "ownerReferences": [{"kind": "Deployment", "name": role, "controller": True}],
        }})
    return rows


class LifecycleTests(unittest.TestCase):
    def test_all_30_slots_are_frozen_and_unique(self):
        rows = [life.slot_by_position(i) for i in range(1, 31)]
        self.assertEqual(len({r["run_id"] for r in rows}), 30)
        self.assertEqual([r["scenario"] for r in rows[:6]],
                         ["C2", "C3", "C4", "C3", "C4", "C2"])
        self.assertEqual({r["measurement_mode"] for r in rows}, {"timing_only"})
        self.assertEqual({r["requests"] for r in rows}, {1000})

    def test_out_of_range_positions_are_refused(self):
        for value in (0, 31, "1", 1.0, True):
            with self.assertRaises(ValueError):
                life.slot_by_position(value)

    def test_paths_never_reuse_sacrificial_s01(self):
        slot = life.slot_by_position(1)
        paths = life.paths_for(slot, "C:/Users/test", "D:/TCC2-Backup")
        self.assertEqual(slot["run_id"], "e11-c2-m01-b01")
        self.assertIn("e11-c2-m01-b01", str(paths["primary"]))
        self.assertNotIn("m01-s01", str(paths["primary"]))
        self.assertEqual(paths["primary"].name, "resultado.zip")
        self.assertTrue(paths["backup"].name.endswith(".zip"))

    def test_namespaced_kube_inventory_c4_passes(self):
        slot = life.slot_by_position(3)
        pods = {"attribute-source": {"name": "as-pod"},
                "logic-engine": {"name": "le-pod"},
                "rule-executor": {"name": "re-pod"},
                "client": {"name": "e11-benchmark-client"}}
        def reader(*args):
            self.assertEqual(args[0:5], (
                "kubectl", "--context", "kind-tcc2-pon", "-n",
                slot["resource_base"]))
            return json.dumps({"items": pod_inventory(slot["resource_base"])})
        self.assertEqual(life.verify_kube_objects(slot, {"pods": pods}, reader), 16)

    def test_extra_kube_object_blocks(self):
        slot = life.slot_by_position(3)
        pods = {"attribute-source": {"name": "as-pod"},
                "logic-engine": {"name": "le-pod"},
                "rule-executor": {"name": "re-pod"},
                "client": {"name": "e11-benchmark-client"}}
        rows = pod_inventory(slot["resource_base"])
        rows.append({"kind": "Secret", "metadata": {
            "name": "foreign", "namespace": slot["resource_base"]}})
        with self.assertRaisesRegex(ValueError, "adicionais"):
            life.verify_kube_objects(
                slot, {"pods": pods}, lambda *args: json.dumps({"items": rows}))

    def test_no_main_execution_without_code_release(self):
        slot = life.slot_by_position(1)
        self.assertFalse(life.MAIN_CAMPAIGN_ENABLED)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "bloqueada"):
                life.execute_run(1, root, root, root / "inputs.jsonl",
                                 SHA, life.approval_phrase("RUN", slot),
                                 empty_inventory, approved_capacity,
                                 lambda *args: self.fail("nunca executar"))
            self.assertFalse((root / "TCC2-Evidencias" / "E11-M01").exists())

    def test_no_main_retirement_without_code_release(self):
        slot = life.slot_by_position(1)
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "bloqueada"):
                life.execute_retirement(
                    1, tmp, tmp, SHA,
                    life.approval_phrase("RETIRE", slot),
                    empty_inventory,
                    lambda *args: self.fail("nunca executar"))

    def test_run_consent_refused_even_in_synthetic_release(self):
        with patch.object(life, "MAIN_CAMPAIGN_ENABLED", True):
            with TemporaryDirectory() as tmp:
                with self.assertRaisesRegex(ValueError, "consentimento"):
                    life.execute_run(1, tmp, tmp, "fixture", SHA, "NO",
                                     empty_inventory, approved_capacity,
                                     lambda *args: self.fail("nunca executar"))

    def test_future_artifact_blocks_slot_one(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            next_slot = life.slot_by_position(2)
            p = life.paths_for(next_slot, root, root)
            p["root"].mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "posterior"):
                life.assert_prior_completed(1, root, root)

    def test_slot_two_requires_completed_first_retirement(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "journal"):
                life.assert_prior_completed(2, tmp, tmp)

    def test_only_one_new_m01_docker_bench_allowed(self):
        slot = life.slot_by_position(1)
        names = set(life.exact_names(slot).values())
        def reader(*args):
            if args == ("docker", "ps", "-a", "--format", "{{.Names}}"):
                return "\n".join(sorted(names))
            if args == ("docker", "network", "ls", "--format", "{{.Name}}"):
                return slot["resource_base"]
            return empty_inventory(*args)
        self.assertEqual(life.check_live_slot_only(slot, reader)["docker"], names)

    def test_extra_new_docker_container_even_stopped_blocks(self):
        slot = life.slot_by_position(1)
        names = set(life.exact_names(slot).values())
        def reader(*args):
            if args == ("docker", "ps", "-a", "--format", "{{.Names}}"):
                return "\n".join(sorted(names |
                            {"tcc2-pon-e11-c2-m01-b02-logic-engine"}))
            if args == ("docker", "network", "ls", "--format", "{{.Name}}"):
                return slot["resource_base"]
            return empty_inventory(*args)
        with self.assertRaisesRegex(ValueError, "unica"):
            life.check_live_slot_only(slot, reader)

    def test_unexpected_m01_role_also_blocks(self):
        slot = life.slot_by_position(1)
        names = set(life.exact_names(slot).values())
        names.add("tcc2-pon-e11-c2-m01-b01-foreign-helper")
        def reader(*args):
            if args == ("docker", "ps", "-a", "--format", "{{.Names}}"):
                return "\n".join(sorted(names))
            if args == ("docker", "network", "ls", "--format", "{{.Name}}"):
                return slot["resource_base"]
            return empty_inventory(*args)
        with self.assertRaisesRegex(ValueError, "unica"):
            life.check_live_slot_only(slot, reader)

    def test_dirty_git_fails_plan_before_any_mutation(self):
        def dirty_reader(*argv):
            if argv == ("git", "status", "--porcelain"):
                return "M benchmark/runner.py"
            return empty_inventory(*argv)
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "suja"):
                life.run_sequence_preflight(
                    1, tmp, tmp, "fixture", dirty_reader, approved_capacity)

    def test_run_preflight_pass_readonly_only(self):
        with TemporaryDirectory() as tmp, patch.object(
            life, "sha256_file", return_value=life.FIXTURE_SHA
        ), patch.object(
            life, "check_completed_sacrificial_archives",
            return_value={"C2": {}, "C3": {}, "C4": {}}
        ), patch.object(
            life, "assess_capacity",
            return_value={"status": "CAPACITY_SAFETY_GATE_PASS_NOT_PERFORMANCE_APPROVAL"}
        ):
            result = life.run_sequence_preflight(
                1, tmp, tmp, "fixture", empty_inventory, approved_capacity)
            self.assertEqual(result["status"], "M01_SLOT_PLAN_ONLY")
            self.assertEqual(result["slot"]["run_id"], "e11-c2-m01-b01")
            self.assertFalse(result["start_authorized"])
            self.assertEqual(result["commands"], [])

    def test_run_failure_journal_and_never_retries(self):
        with TemporaryDirectory() as tmp, patch.object(
            life, "MAIN_CAMPAIGN_ENABLED", True
        ), patch.object(
            life, "run_sequence_preflight", return_value={"status": "M01_SLOT_PLAN_ONLY"}
        ), patch.object(
            life, "inspect_global_exclusivity", return_value={}
        ), patch.object(
            life, "verify_storage_before_run", return_value=True
        ):
            base = Path(tmp)
            backup = base / "backups" / "E11-M01"
            backup.mkdir(parents=True)
            slot = life.slot_by_position(1)
            counter = []
            def fail(*args):
                counter.append(args)
                raise RuntimeError("falha de runner sintetica")
            with self.assertRaisesRegex(RuntimeError, "runner sintetica"):
                life.execute_run(
                    1, base, base / "backups", "fixture", SHA,
                    life.approval_phrase("RUN", slot), empty_inventory,
                    approved_capacity, fail)
            journal_path = life.paths_for(slot, base, base / "backups")["run_journal"]
            lines = [json.loads(x) for x in journal_path.read_text().splitlines()]
            self.assertEqual(lines[-1]["stage"], "INTERRUPTED_DO_NOT_RETRY")
            self.assertEqual(len(counter), 1)
            with self.assertRaises((FileExistsError, ValueError)):
                life.execute_run(
                    1, base, base / "backups", "fixture", SHA,
                    life.approval_phrase("RUN", slot), empty_inventory,
                    approved_capacity, fail)
            self.assertEqual(len(counter), 1)

    def test_run_pass_writes_backup_and_keeps_resources(self):
        with TemporaryDirectory() as tmp, patch.object(
            life, "MAIN_CAMPAIGN_ENABLED", True
        ), patch.object(
            life, "run_sequence_preflight", return_value={"status": "M01_SLOT_PLAN_ONLY"}
        ), patch.object(
            life, "inspect_global_exclusivity", return_value={}
        ), patch.object(
            life, "verify_storage_before_run", return_value=True
        ), patch.object(
            life, "audit_archive", side_effect=valid_audit
        ), patch.object(
            life, "compare_backup_pair", side_effect=valid_backup
        ):
            base = Path(tmp)
            backup_root = base / "backups"
            (backup_root / "E11-M01").mkdir(parents=True)
            slot = life.slot_by_position(1)
            paths = life.paths_for(slot, base, backup_root)
            actions = []
            def action(*args):
                actions.append(args)
                paths["primary"].write_bytes(b"test-evidence-only")
                return "runner synthetically passed"
            result = life.execute_run(
                1, base, backup_root, "fixture", SHA,
                life.approval_phrase("RUN", slot), empty_inventory,
                approved_capacity, action)
            self.assertEqual(result["status"], "M01_RUN_PASS_BACKED_UP")
            self.assertEqual(paths["backup"].read_bytes(), b"test-evidence-only")
            self.assertFalse(paths["retire_journal"].exists())
            self.assertEqual(len(actions), 1)
            end = life.last_event(paths["run_journal"])
            self.assertEqual(end["status"], "M01_RUN_PASS_BACKED_UP")

    def test_kube_retirement_uses_uid_precondition_and_keeps_old_uids(self):
        slot = life.slot_by_position(3)
        uid = "uid-of-new-c4"
        owner = {"namespace": {"name": slot["resource_base"], "uid": uid}}
        packet = {"status": "M01_RETIREMENT_REVIEW_ONLY_PASS",
                  "zip_sha256": HASH, "resource_immutable_ids": {
                      "namespace_uid": uid}, "ownership": owner}
        with TemporaryDirectory() as tmp, patch.object(
            life, "MAIN_CAMPAIGN_ENABLED", True
        ), patch.object(
            life, "review_retirement", return_value=packet
        ), patch.object(
            life, "assert_prior_completed", return_value=True
        ), patch.object(
            life, "namespaces", side_effect=[
                {"default": "old", slot["resource_base"]: uid},
                {"default": "old", slot["resource_base"]: uid},
                {"default": "old"},
            ]
        ), patch.object(
            life, "sha256_file", return_value=HASH
        ):
            backup_root = Path(tmp) / "backups"
            (backup_root / "E11-M01").mkdir(parents=True)
            actions = []
            def action(*args):
                actions.append(args)
                return "ok"
            result = life.execute_retirement(
                3, tmp, backup_root, SHA,
                life.approval_phrase("RETIRE", slot),
                empty_inventory, action)
            self.assertEqual(result["status"], "M01_RETIREMENT_COMPLETE")
            delete = [x for x in actions if "delete" in x]
            self.assertEqual(len(delete), 1)
            self.assertEqual(delete[0][-3:-1], (
                "/api/v1/namespaces/" + slot["resource_base"], "-f"))
            opt = life.paths_for(slot, tmp, backup_root)["delete_options"]
            self.assertEqual(json.loads(opt.read_text())["preconditions"]["uid"], uid)
            self.assertEqual(len(actions), 2)
            self.assertEqual(life.last_event(
                life.paths_for(slot, tmp, backup_root)["retire_journal"]
            )["status"], "M01_RETIREMENT_COMPLETE")

    def test_duplicate_retirement_journal_blocks_any_action(self):
        slot = life.slot_by_position(1)
        with TemporaryDirectory() as tmp, patch.object(
            life, "MAIN_CAMPAIGN_ENABLED", True
        ), patch.object(
            life, "assert_prior_completed", return_value=True
        ):
            root = Path(tmp)
            dst = life.paths_for(slot, root, root)
            dst["backup_root"].mkdir(parents=True)
            dst["retire_journal"].write_text("old attempt", encoding="utf-8")
            action_calls = []
            with self.assertRaisesRegex(ValueError, "registrada"):
                life.execute_retirement(
                    1, root, root, SHA, life.approval_phrase("RETIRE", slot),
                    empty_inventory, lambda *argv: action_calls.append(argv))
            self.assertEqual(action_calls, [])

    def test_kube_retirement_action_failure_is_journaled_no_retry(self):
        slot = life.slot_by_position(3)
        uid = "uid-of-new-c4"
        packet = {"zip_sha256": HASH,
                  "resource_immutable_ids": {"namespace_uid": uid},
                  "ownership": {"namespace": {
                      "name": slot["resource_base"], "uid": uid}},
                  "status": "M01_RETIREMENT_REVIEW_ONLY_PASS"}
        with TemporaryDirectory() as tmp, patch.object(
            life, "MAIN_CAMPAIGN_ENABLED", True
        ), patch.object(
            life, "assert_prior_completed", return_value=True
        ), patch.object(
            life, "review_retirement", return_value=packet
        ), patch.object(
            life, "namespaces", side_effect=[
                {"default": "old", slot["resource_base"]: uid},
                {"default": "old", slot["resource_base"]: uid},
            ]
        ):
            root = Path(tmp)
            paths = life.paths_for(slot, root, root)
            paths["backup_root"].mkdir(parents=True)
            actions = []
            def failing_action(*args):
                actions.append(args)
                raise RuntimeError("falha DELETE sintetica")
            with self.assertRaisesRegex(RuntimeError, "DELETE sintetica"):
                life.execute_retirement(
                    3, root, root, SHA, life.approval_phrase("RETIRE", slot),
                    empty_inventory, failing_action)
            self.assertEqual(len(actions), 1)
            last = life.last_event(paths["retire_journal"])
            self.assertEqual(last["stage"], "INTERRUPTED_DO_NOT_RETRY")
            with self.assertRaises(ValueError):
                life.execute_retirement(
                    3, root, root, SHA, life.approval_phrase("RETIRE", slot),
                    empty_inventory, failing_action)
            self.assertEqual(len(actions), 1)

    def test_readonly_retirement_requires_matching_archived_docker_ids(self):
        slot = life.slot_by_position(1)
        owner = {
            "status": "NEW_BENCH_OWNERSHIP_READONLY_PASS", "scenario": "C2",
            "run_id": slot["run_id"],
            "network": {"name": slot["resource_base"], "id": "a"*64},
            "containers": {r: {
                "name": life.exact_names(slot)[r], "id": str(i+1)*64,
                "image_id": life.IMAGE_ID,
            } for i, r in enumerate(life.ROLES)},
            "delete_authorized": False, "commands": [],
        }
        class FakeZip:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, name):
                self.assert_owned = name
                return json.dumps({
                    "network": owner["network"],
                    "containers": {"client": {"id": "f"*64}},
                }).encode()
        with TemporaryDirectory() as tmp, patch.object(
            life, "audit_archive", side_effect=valid_audit
        ), patch.object(
            life, "compare_backup_pair", side_effect=valid_backup
        ), patch.object(
            life, "require_complete", return_value={"zip_sha256": HASH}
        ), patch.object(
            life, "capture_docker_ownership", return_value=owner
        ), patch.object(
            life, "ZipFile", return_value=FakeZip()
        ):
            paths = life.paths_for(slot, tmp, tmp)
            with self.assertRaisesRegex(ValueError, "diferentes do ZIP"):
                life.review_retirement(slot, paths, empty_inventory)

    def test_same_filesystem_backup_blocks_before_mutation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            backup = root / "backups" / "E11-M01"
            backup.mkdir(parents=True)
            slot = life.slot_by_position(1)
            with self.assertRaisesRegex(ValueError, "outro volume"):
                life.verify_storage_before_run(
                    life.paths_for(slot, root, root / "backups"))

    def test_current_zip_sha_mismatch_in_journal_blocks_retirement_review(self):
        slot = life.slot_by_position(1)
        with TemporaryDirectory() as tmp, patch.object(
            life, "audit_archive", side_effect=valid_audit
        ), patch.object(
            life, "compare_backup_pair", side_effect=valid_backup
        ), patch.object(
            life, "require_complete", return_value={"zip_sha256": "0"*64}
        ):
            with self.assertRaisesRegex(ValueError, "SHA do ZIP"):
                life.review_retirement(
                    slot, life.paths_for(slot, tmp, tmp), empty_inventory)

    def test_future_delete_options_orphan_blocks_current_slot(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = life.paths_for(life.slot_by_position(2), root, root)
            target["delete_options"].parent.mkdir(parents=True)
            target["delete_options"].write_text(
                '{"preconditions":{"uid":"unknown"}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "posterior"):
                life.assert_prior_completed(1, root, root)

    def test_kube_run_synthetic_creates_only_new_ns_and_backups(self):
        slot = life.slot_by_position(3)
        with TemporaryDirectory() as tmp, patch.object(
            life, "MAIN_CAMPAIGN_ENABLED", True
        ), patch.object(
            life, "run_sequence_preflight", return_value={"status": "M01_SLOT_PLAN_ONLY"}
        ), patch.object(
            life, "inspect_global_exclusivity", return_value={}
        ), patch.object(
            life, "verify_storage_before_run", return_value=True
        ), patch.object(
            life, "capture_kind_ownership", return_value={
                "namespace": {"name": slot["resource_base"], "uid": "new-uid"}
            }
        ), patch.object(
            life, "audit_archive", side_effect=valid_audit
        ), patch.object(
            life, "compare_backup_pair", side_effect=valid_backup
        ), patch(
            "benchmark.prepare.render",
            return_value=(slot["resource_base"], "kind: Namespace\nmetadata:\n  name: " +
                          slot["resource_base"] + "\n")
        ):
            base = Path(tmp)
            backup_root = base / "backups"
            (backup_root / "E11-M01").mkdir(parents=True)
            p = life.paths_for(slot, base, backup_root)
            actions = []
            def action(*args):
                actions.append(args)
                if "benchmark.runner" in args:
                    p["primary"].write_bytes(b"synthetic-zip-only")
                return "mock-command-pass"
            result = life.execute_run(
                3, base, backup_root, "fixture", SHA,
                life.approval_phrase("RUN", slot), empty_inventory,
                approved_capacity, action)
            self.assertEqual(result["status"], "M01_RUN_PASS_BACKED_UP")
            self.assertEqual(p["backup"].read_bytes(), b"synthetic-zip-only")
            applies = [x for x in actions if x[0] == "kubectl" and "apply" in x]
            self.assertEqual(len(applies), 2)
            self.assertTrue(all(str(p["manifest"]) in x for x in applies))
            self.assertEqual(sum("benchmark.runner" in x for x in actions), 1)
            self.assertFalse(any("delete" in x for x in actions))
            self.assertFalse(p["retire_journal"].exists())

    def test_docker_retirement_synthetic_targets_only_four_ids_and_network(self):
        slot = life.slot_by_position(1)
        network_id = "a" * 64
        names = life.exact_names(slot)
        container_ids = {role: str(i+1) * 64
                         for i, role in enumerate(life.ROLES)}
        owner = {
            "network": {"name": slot["resource_base"], "id": network_id},
            "containers": {role: {"name": names[role], "id": container_ids[role],
                                   "image_id": life.IMAGE_ID}
                           for role in life.ROLES},
        }
        packet = {
            "status": "M01_RETIREMENT_REVIEW_ONLY_PASS",
            "zip_sha256": HASH,
            "resource_immutable_ids": {
                "network_id": network_id, "container_ids": container_ids,
            },
            "ownership": owner,
        }
        with TemporaryDirectory() as tmp, patch.object(
            life, "MAIN_CAMPAIGN_ENABLED", True
        ), patch.object(
            life, "assert_prior_completed", return_value=True
        ), patch.object(
            life, "review_retirement", return_value=packet
        ), patch.object(
            life, "verify_c2_network", return_value=None
        ), patch.object(
            life, "inspect_c2_container", return_value=None
        ), patch.object(
            life, "sha256_file", return_value=HASH
        ):
            base = Path(tmp)
            (base / "E11-M01").mkdir(parents=True)
            actions = []
            def action(*args):
                actions.append(args)
                return "synthetic-ok"
            result = life.execute_retirement(
                1, base, base, SHA,
                life.approval_phrase("RETIRE", slot),
                empty_inventory, action)
            self.assertEqual(result["status"], "M01_RETIREMENT_COMPLETE")
            self.assertEqual(len(actions), 9)
            stop = [x for x in actions if x[:3] == (
                "docker", "container", "stop")]
            rm = [x for x in actions if x[:3] == (
                "docker", "container", "rm")]
            network = [x for x in actions if x[:3] == (
                "docker", "network", "rm")]
            self.assertEqual(len(stop), 4)
            self.assertEqual(len(rm), 4)
            self.assertEqual(len(network), 1)
            self.assertEqual({x[-1] for x in stop},
                             set(container_ids.values()))
            self.assertEqual({x[-1] for x in rm},
                             set(container_ids.values()))
            self.assertEqual(network[0][-1], network_id)
            self.assertEqual(life.last_event(
                life.paths_for(slot, base, base)["retire_journal"]
            )["status"], "M01_RETIREMENT_COMPLETE")

    def test_retirement_refuses_incorrect_approval_before_mutation(self):
        with patch.object(life, "MAIN_CAMPAIGN_ENABLED", True):
            with TemporaryDirectory() as tmp:
                with self.assertRaisesRegex(ValueError, "consentimento"):
                    life.execute_retirement(
                        1, tmp, tmp, SHA, "NOT_APPROVED",
                        empty_inventory,
                        lambda *args: self.fail("nunca executar"))


if __name__ == "__main__":
    unittest.main()
