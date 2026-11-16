"""E11-M00C: testes injetados do inventario, sem processos externos."""
import json
from types import SimpleNamespace
import unittest

from benchmark.environment_snapshot import capture_environment, IMAGE_ID


def disk(_):
    return SimpleNamespace(total=1000000000, free=600000000)


def command_map(windows=False, kube=False):
    d = {
        ("docker", "info", "--format", "{{.CgroupVersion}}|{{.NCPU}}|{{.MemTotal}}"): "2|8|8245637120",
        ("docker", "image", "inspect", "tcc2-pon:c2-e08-dbefcd2cf3d2", "--format", "{{.Id}}"): IMAGE_ID,
        ("git", "rev-parse", "HEAD"): "a" * 40,
        ("docker", "context", "show"): "desktop-linux",
    }
    if kube:
        d[("kubectl", "--context", "kind-tcc2-pon", "get", "nodes", "-o", "json")] = json.dumps({
            "items": [{"metadata": {"name": n, "uid": n}, "status": {
                "conditions": [{"type": "Ready", "status": "True"}],
                "allocatable": {"cpu": "8", "memory": "8052380Ki"}}}
                for n in ("tcc2-pon-worker", "tcc2-pon-control-plane")]})
    if windows:
        d["powershell.exe"] = json.dumps({"total_bytes": 17000000000, "free_bytes": 2500000000})
    def read(*args):
        return d[args[0]] if args[0] == "powershell.exe" else d[args]
    return read


class EnvironmentSnapshotTests(unittest.TestCase):
    def test_docker_only_baseline_readonly(self):
        result = capture_environment("C2", "e11-c2-m01-b01",
                                     reader=command_map(), disk_usage=disk,
                                     os_name="Linux")
        self.assertEqual(result["status"], "BASELINE_READ_ONLY_NOT_CAPACITY_APPROVAL")
        self.assertEqual(result["docker_cgroup_version"], "2")
        self.assertEqual(result["docker_mem_total_bytes"], 8245637120)
        self.assertEqual(result["image_id"], IMAGE_ID)
        self.assertEqual(result["disk_free_bytes"], 600000000)
        self.assertFalse(result["cpu_ram_comparison_approved"])

    def test_kube_nodes_reported_not_added(self):
        result = capture_environment("C4", "e11-c4-m01-b01",
                                     reader=command_map(kube=True),
                                     disk_usage=disk, os_name="Linux")
        self.assertEqual(len(result["node_allocatable"]), 2)
        self.assertEqual(result["node_allocatable"]["tcc2-pon-worker"]
                         ["allocatable"]["cpu"], "8")

    def test_windows_free_ram_from_readonly_shell(self):
        result = capture_environment("C3", "e11-c3-m01-b01",
                                     reader=command_map(windows=True, kube=True),
                                     disk_usage=disk, os_name="Windows")
        self.assertEqual(result["windows_host_ram_free_bytes"], 2500000000)

    def test_image_mismatch_fails_closed(self):
        good = command_map()
        def modified(*args):
            if args[:3] == ("docker", "image", "inspect"):
                return "sha256:wrong"
            return good(*args)
        with self.assertRaises(ValueError):
            capture_environment("C2", "e11-c2-m01-b01", reader=modified,
                                disk_usage=disk, os_name="Linux")

    def test_missing_node_or_invalid_ram_fails(self):
        good = command_map(kube=True)
        def missing(*args):
            if args[0] == "kubectl":
                return json.dumps({"items": []})
            return good(*args)
        with self.assertRaises(ValueError):
            capture_environment("C3", "e11-c3-m01-b01", reader=missing,
                                disk_usage=disk, os_name="Linux")
        read = command_map(windows=True)
        def invalid_ram(*args):
            if args[0] == "powershell.exe":
                return json.dumps({"total_bytes": 10, "free_bytes": 20})
            return read(*args)
        with self.assertRaises(ValueError):
            capture_environment("C2", "e11-c2-m01-b01", reader=invalid_ram,
                                disk_usage=disk, os_name="Windows")


if __name__ == "__main__":
    unittest.main()
