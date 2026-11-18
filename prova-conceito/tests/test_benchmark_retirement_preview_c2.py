"""E11-M00F: testes sintéticos de preview; SEM stop/rm/alteração Docker."""
import json
import unittest
from unittest.mock import patch

from benchmark.retirement_preview_c2 import (
    BASE, RUN_ID, ROLES, plan_s01_retirement, verify_live_inventory,
)


def sample_owner():
    containers = {}
    for n, role in enumerate(ROLES):
        containers[role] = {
            "name": BASE + ("-benchmark-client" if role == "client" else "-" + role),
            "id": f"{n + 1:064x}",
            "image_id": "sha256:" + "e" * 64,
        }
    return {
        "status": "NEW_BENCH_OWNERSHIP_READONLY_PASS",
        "scenario": "C2", "run_id": RUN_ID,
        "network": {"name": BASE, "id": "a" * 64},
        "containers": containers,
        "delete_authorized": False, "commands": [],
    }


def make_query(owner=None, mutate=None):
    owner = owner or sample_owner()
    endpoints = {v["id"]: {"Name": v["name"]}
                 for v in owner["containers"].values()}
    network = {"Id": owner["network"]["id"], "Name": BASE,
               "Containers": endpoints}
    data = {
        "names": [v["name"] for v in owner["containers"].values()]
                 + ["tcc2-v06-logic-engine",
                    "tcc2-pon-e11-c2-p20261115-232946-attribute-source"],
        "networks": ["bridge", BASE, "kind", "tcc2-pon-c2-v06"],
        "namespaces": ["default", "tcc2-pon", "tcc2-pon-c4"],
        "network": network,
        "by_id": {v["id"]: {
            "Id": v["id"], "Name": "/" + v["name"],
            "NetworkSettings": {"Networks": {BASE: {"NetworkID": network["Id"]}}},
        } for v in owner["containers"].values()},
    }
    if mutate:
        mutate(data)
    def query(*args):
        if args == ("docker", "ps", "-a", "--format", "{{.Names}}"):
            return "\n".join(data["names"])
        if args == ("docker", "network", "ls", "--format", "{{.Name}}"):
            return "\n".join(data["networks"])
        if args == ("kubectl", "--context", "kind-tcc2-pon",
                    "get", "namespaces", "-o", "json"):
            return json.dumps({"items": [
                {"metadata": {"name": name}} for name in data["namespaces"]]})
        if args == ("docker", "network", "inspect", BASE):
            return json.dumps([data["network"]])
        if len(args) == 3 and args[:2] == ("docker", "inspect"):
            return json.dumps([data["by_id"][args[2]]])
        raise AssertionError(f"consulta inesperada: {args!r}")
    return query


class FakeZip:
    def __init__(self, owner):
        self.owner = owner
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False
    def read(self, name):
        if name != "ownership-start.json":
            raise AssertionError("somente ownership-start.json permitido")
        return json.dumps(self.owner).encode()


class RetirementPreviewTests(unittest.TestCase):
    def test_only_exact_new_resources_and_historical_ignored(self):
        owner = sample_owner()
        result = verify_live_inventory(owner, make_query(owner))
        self.assertEqual(result["containers"], 4)
        self.assertEqual(result["networks"], 1)
        self.assertEqual(result["unexpected_new_resources"], 0)

    def test_another_new_stopped_container_blocks(self):
        def change(d):
            d["names"].append("tcc2-pon-e11-c2-m01-s02-logic-engine")
        with self.assertRaises(ValueError):
            verify_live_inventory(sample_owner(), make_query(mutate=change))

    def test_another_new_network_blocks(self):
        def change(d):
            d["networks"].append("tcc2-pon-e11-c2-m01-s02")
        with self.assertRaises(ValueError):
            verify_live_inventory(sample_owner(), make_query(mutate=change))

    def test_new_kubernetes_namespace_blocks(self):
        def change(d):
            d["namespaces"].append("tcc2-pon-e11-c4-m01-s02")
        with self.assertRaises(ValueError):
            verify_live_inventory(sample_owner(), make_query(mutate=change))

    def test_foreign_endpoint_blocks(self):
        def change(d):
            d["network"]["Containers"]["f" * 64] = {"Name": "foreign"}
        with self.assertRaises(ValueError):
            verify_live_inventory(sample_owner(), make_query(mutate=change))

    def test_changed_container_network_blocks(self):
        def change(d):
            key = next(iter(d["by_id"]))
            d["by_id"][key]["NetworkSettings"]["Networks"]["bridge"] = {}
        with self.assertRaises(ValueError):
            verify_live_inventory(sample_owner(), make_query(mutate=change))

    def test_changed_network_id_blocks(self):
        def change(d):
            d["network"]["Id"] = "b" * 64
        with self.assertRaises(ValueError):
            verify_live_inventory(sample_owner(), make_query(mutate=change))

    def test_plan_consolidates_but_never_authorizes(self):
        owner = sample_owner()
        audit = {"status": "ZIP_INTEGRITY_VERIFIED_NOT_DELETION_AUTHORIZATION",
                 "zip_sha256": "a" * 64, "run_id": RUN_ID, "scenario": "C2",
                 "delete_authorized": False}
        backup = {"status": "BACKUP_BYTES_VERIFIED_NO_CLEANUP_AUTHORIZATION",
                  "different_filesystem_volume": True, "zip_sha256": "a" * 64}
        review = {
            "expected_new_resource_names": {"network": BASE},
            "resource_immutable_ids": {"network_id": owner["network"]["id"],
               "container_ids": {r: owner["containers"][r]["id"] for r in ROLES}},
            "delete_authorized": False, "commands": [],
        }
        with patch("benchmark.retirement_preview_c2.audit_archive",
                   return_value=audit), patch(
                   "benchmark.retirement_preview_c2.compare_backup_pair",
                   return_value=backup), patch(
                   "benchmark.retirement_preview_c2.capture_docker_ownership",
                   return_value=owner), patch(
                   "benchmark.retirement_preview_c2.review_retirement_packet",
                   return_value=review), patch(
                   "benchmark.retirement_preview_c2.ZipFile",
                   return_value=FakeZip(owner)):
            result = plan_s01_retirement("orig.zip", "backup.zip",
                                         make_query(owner))
        self.assertEqual(result["status"],
                         "RETIREMENT_PREVIEW_READONLY_PASS_NOT_AUTHORIZATION")
        self.assertFalse(result["delete_authorized"])
        self.assertEqual(result["commands"], [])
        self.assertTrue(result["requires_explicit_operator_approval"])
        self.assertTrue(result["requires_tested_execution_procedure"])

    def test_plan_wrong_archived_id_blocks(self):
        owner = sample_owner()
        archived = sample_owner()
        archived["containers"]["client"]["id"] = "f" * 64
        with patch("benchmark.retirement_preview_c2.audit_archive",
                   return_value={"zip_sha256": "a" * 64}), patch(
                   "benchmark.retirement_preview_c2.compare_backup_pair",
                   return_value={"different_filesystem_volume": True}), patch(
                   "benchmark.retirement_preview_c2.capture_docker_ownership",
                   return_value=owner), patch(
                   "benchmark.retirement_preview_c2.ZipFile",
                   return_value=FakeZip(archived)):
            with self.assertRaises(ValueError):
                plan_s01_retirement("orig.zip", "backup.zip", make_query(owner))

    def test_plan_same_volume_blocks(self):
        with patch("benchmark.retirement_preview_c2.audit_archive",
                   return_value={"zip_sha256": "a" * 64}), patch(
                   "benchmark.retirement_preview_c2.compare_backup_pair",
                   return_value={"different_filesystem_volume": False}):
            with self.assertRaises(ValueError):
                plan_s01_retirement("orig.zip", "backup.zip", make_query())


if __name__ == "__main__":
    unittest.main()
