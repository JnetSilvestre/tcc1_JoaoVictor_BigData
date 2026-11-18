"""E11-M00G: testes sinteticos de encerramento C3-S01, sem acesso ao cluster."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from benchmark.retirement_execute_c3_s01 import (
    APPROVAL, DELETE_OPTIONS, JOURNAL, NS, UID, ZIP_SHA,
    apply_approved_retirement, verify_inventory,
)

HEAD = "a" * 40


def packet():
    return {"status": "C3_S01_RETIREMENT_READONLY_PASS_NOT_AUTHORIZED",
            "namespace": NS, "namespace_uid": UID, "zip_sha256": ZIP_SHA,
            "delete_authorized": False, "commands": []}


def objects():
    rows = []
    for kind, names in (
        ("Pod", ["source-pod", "logic-pod", "rule-pod", "e11-benchmark-client"]),
        ("Deployment", ["attribute-source", "logic-engine", "rule-executor"]),
        ("Service", ["attribute-source", "logic-engine", "rule-executor"]),
        ("ConfigMap", ["e11-c3-config", "kube-root-ca.crt"]),
        ("ServiceAccount", ["default"]),
    ):
        rows += [{"kind": kind, "metadata": {"name": name, "namespace": NS}}
                 for name in names]
    for role in ("attribute-source", "logic-engine", "rule-executor"):
        rows.append({"kind": "ReplicaSet", "metadata": {
            "name": role + "-replicaset", "namespace": NS,
            "labels": {"app": role},
            "ownerReferences": [{"kind": "Deployment", "name": role, "controller": True}],
        }})
    return rows


def archived():
    return {"pods": {
        "attribute-source": {"name": "source-pod"},
        "logic-engine": {"name": "logic-pod"},
        "rule-executor": {"name": "rule-pod"},
        "client": {"name": "e11-benchmark-client"},
    }}


def query_inventory(rows):
    def query(*args):
        if args[:5] != ("kubectl", "--context", "kind-tcc2-pon", "-n", NS):
            raise AssertionError("Consulta fora do namespace C3-S01")
        return json.dumps({"items": rows})
    return query


class C3S01RetirementTests(unittest.TestCase):
    def test_inventory_only_known_workloads_passes(self):
        result = verify_inventory(query_inventory(objects()), archived())
        self.assertEqual(result["replicasets"], 3)

    def test_foreign_pod_blocks(self):
        rows = objects()
        rows.append({"kind": "Pod", "metadata": {
            "name": "foreign", "namespace": NS,
        }})
        with self.assertRaisesRegex(ValueError, "Pods adicionais"):
            verify_inventory(query_inventory(rows), archived())

    def test_foreign_resource_blocks(self):
        rows = objects()
        rows.append({"kind": "Secret", "metadata": {
            "name": "foreign", "namespace": NS,
        }})
        with self.assertRaisesRegex(ValueError, "alheio"):
            verify_inventory(query_inventory(rows), archived())

    def test_replicaset_without_owner_blocks(self):
        rows = objects()
        rows[-1]["metadata"]["ownerReferences"] = []
        with self.assertRaisesRegex(ValueError, "ReplicaSet"):
            verify_inventory(query_inventory(rows), archived())

    def test_consent_refusal_no_mutation_or_journal(self):
        with TemporaryDirectory() as temp, patch(
            "benchmark.retirement_execute_c3_s01.preview",
            return_value=packet()
        ):
            calls = []
            root = Path(temp)
            with self.assertRaisesRegex(ValueError, "aceite"):
                apply_approved_retirement(
                    "primary.zip", "backup.zip", "NO", HEAD,
                    lambda *args: "", lambda *args: calls.append(args),
                    HEAD, root / JOURNAL, root / DELETE_OPTIONS)
            self.assertEqual(calls, [])
            self.assertFalse((root / JOURNAL).exists())

    def test_wrong_head_no_mutation(self):
        with TemporaryDirectory() as temp:
            calls = []
            with self.assertRaisesRegex(ValueError, "SHA"):
                apply_approved_retirement(
                    "primary.zip", "backup.zip", APPROVAL, "b" * 40,
                    lambda *args: "", lambda *args: calls.append(args),
                    HEAD, Path(temp) / JOURNAL, Path(temp) / DELETE_OPTIONS)
            self.assertEqual(calls, [])

    def test_full_mock_issues_one_uid_preconditioned_delete(self):
        with TemporaryDirectory() as temp, patch(
            "benchmark.retirement_execute_c3_s01.preview",
            return_value=packet()
        ), patch(
            "benchmark.retirement_execute_c3_s01.namespaces",
            side_effect=[
                {"default": "old", NS: UID},
                {"default": "old", NS: UID},
                {"default": "old"},
            ]
        ), patch(
            "benchmark.retirement_execute_c3_s01.sha256_file",
            return_value=ZIP_SHA
        ):
            root = Path(temp)
            calls = []
            def action(*args):
                calls.append(args)
                return '{"status":"Success"}'
            result = apply_approved_retirement(
                "primary.zip", "backup.zip", APPROVAL, HEAD,
                lambda *args: "", action,
                HEAD, root / JOURNAL, root / DELETE_OPTIONS)
            self.assertEqual(result["status"], "C3_S01_RETIREMENT_COMPLETE")
            delete = [args for args in calls if "delete" in args]
            self.assertEqual(len(delete), 1)
            self.assertEqual(delete[0][0:4], (
                "kubectl", "--context", "kind-tcc2-pon", "delete"))
            self.assertIn("--raw", delete[0])
            self.assertIn("/api/v1/namespaces/" + NS, delete[0])
            payload = json.loads((root / DELETE_OPTIONS).read_text())
            self.assertEqual(payload["preconditions"]["uid"], UID)
            self.assertEqual(payload["propagationPolicy"], "Foreground")
            journal = [json.loads(line) for line in
                       (root / JOURNAL).read_text(encoding="utf-8").splitlines()]
            self.assertEqual(journal[-1]["stage"], "COMPLETE")
            self.assertEqual(len(calls), 2)

    def test_fail_action_journal_blocks_retry(self):
        with TemporaryDirectory() as temp, patch(
            "benchmark.retirement_execute_c3_s01.preview",
            return_value=packet()
        ), patch(
            "benchmark.retirement_execute_c3_s01.namespaces",
            return_value={"default": "old", NS: UID}
        ):
            root = Path(temp)
            calls = []
            def failed(*args):
                calls.append(args)
                raise RuntimeError("mutacao sintetica falhou")
            with self.assertRaises(RuntimeError):
                apply_approved_retirement(
                    "primary.zip", "backup.zip", APPROVAL, HEAD,
                    lambda *args: "", failed,
                    HEAD, root / JOURNAL, root / DELETE_OPTIONS)
            journal = (root / JOURNAL).read_text(encoding="utf-8")
            self.assertIn("INTERRUPTED_DO_NOT_RETRY", journal)
            with self.assertRaises(ValueError):
                apply_approved_retirement(
                    "primary.zip", "backup.zip", APPROVAL, HEAD,
                    lambda *args: "", failed,
                    HEAD, root / JOURNAL, root / DELETE_OPTIONS)
            self.assertEqual(len(calls), 1)

    def test_existing_journal_blocks(self):
        with TemporaryDirectory() as temp, patch(
            "benchmark.retirement_execute_c3_s01.preview",
            return_value=packet()
        ), patch(
            "benchmark.retirement_execute_c3_s01.namespaces",
            return_value={"default": "old", NS: UID}
        ):
            root = Path(temp)
            (root / JOURNAL).write_text("historic record", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "journal/options"):
                apply_approved_retirement(
                    "primary.zip", "backup.zip", APPROVAL, HEAD,
                    lambda *args: "", lambda *args: "",
                    HEAD, root / JOURNAL, root / DELETE_OPTIONS)

    def test_namespace_change_blocks_before_delete(self):
        with TemporaryDirectory() as temp, patch(
            "benchmark.retirement_execute_c3_s01.preview",
            return_value=packet()
        ), patch(
            "benchmark.retirement_execute_c3_s01.namespaces",
            side_effect=[
                {"default": "old", NS: UID},
                {"default": "replaced", NS: UID},
            ]
        ):
            root = Path(temp)
            actions = []
            with self.assertRaisesRegex(ValueError, "mudou"):
                apply_approved_retirement(
                    "primary.zip", "backup.zip", APPROVAL, HEAD,
                    lambda *args: "", lambda *args: actions.append(args),
                    HEAD, root / JOURNAL, root / DELETE_OPTIONS)
            self.assertEqual(actions, [])


if __name__ == "__main__":
    unittest.main()
