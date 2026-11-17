"""E11-M00C: 8 testes puros com queries injetadas; sem Docker/Kubectl real."""
import json
import unittest

from benchmark.runtime_gate import (
    APP_MEMORY_BYTES, CLIENT_MEMORY_BYTES, CGROUP_READER,
    assess_capacity, capture_effective_quotas, validate_cgroup_v2,
)


def env(ram=4 * 1024 ** 3, disk=25 * 1024 ** 3):
    return {
        "status": "BASELINE_READ_ONLY_NOT_CAPACITY_APPROVAL",
        "docker_cgroup_version": "2", "windows_host_ram_free_bytes": ram,
        "disk_free_bytes": disk,
    }


def sample(memory):
    return {"cpu_max": "50000 100000", "memory_max": str(memory),
            "memory_current": "33554432", "memory_swap_max": "0",
            "memory_events": "low 0\nhigh 0\nmax 0\noom 0\noom_kill 0"}


class RuntimeGateTests(unittest.TestCase):
    def test_host_above_threshold_passes_as_safety_not_approval(self):
        gate = assess_capacity(env())
        self.assertEqual(gate["status"],
                         "CAPACITY_SAFETY_GATE_PASS_NOT_PERFORMANCE_APPROVAL")

    def test_low_windows_ram_blocks_pre_snapshot(self):
        with self.assertRaises(ValueError):
            assess_capacity(env(ram=2 * 1024 ** 3))

    def test_low_disk_or_missing_windows_ram_blocks(self):
        with self.assertRaises(ValueError):
            assess_capacity(env(disk=10 * 1024 ** 3))
        case = env()
        case["windows_host_ram_free_bytes"] = None
        with self.assertRaises(ValueError):
            assess_capacity(case)

    def test_cgroup_service_and_client_limits(self):
        service = validate_cgroup_v2(sample(APP_MEMORY_BYTES), "logic-engine")
        client = validate_cgroup_v2(sample(CLIENT_MEMORY_BYTES), "client")
        self.assertEqual(service["memory_max_bytes"], APP_MEMORY_BYTES)
        self.assertEqual(client["memory_max_bytes"], CLIENT_MEMORY_BYTES)

    def test_cgroup_cpu_unlimited_unequal_and_missing_rejected(self):
        for cpu in ("max 100000", "100000 100000", "", None):
            with self.subTest(cpu=cpu):
                bad = sample(APP_MEMORY_BYTES)
                bad["cpu_max"] = cpu
                with self.assertRaises(ValueError):
                    validate_cgroup_v2(bad, "attribute-source")

    def test_cgroup_memory_mismatch_and_oom_rejected(self):
        with self.assertRaises(ValueError):
            validate_cgroup_v2(sample(CLIENT_MEMORY_BYTES), "attribute-source")
        bad = sample(APP_MEMORY_BYTES)
        bad["memory_events"] = "oom 1\noom_kill 0"
        with self.assertRaises(ValueError):
            validate_cgroup_v2(bad, "rule-executor")

    def test_new_docker_names_only_and_four_readonly_probes(self):
        base = "tcc2-pon-e11-c2-m01-b01-"
        names = {r: base+r for r in
                 ("attribute-source", "logic-engine", "rule-executor")}
        names["client"] = base + "benchmark-client"
        called = []
        def query(*argv):
            called.append(argv)
            role = "client" if "benchmark-client" in argv[2] else "attribute-source"
            return json.dumps(sample(CLIENT_MEMORY_BYTES if role == "client"
                                     else APP_MEMORY_BYTES))
        result = capture_effective_quotas("C2", names=names, query=query)
        self.assertEqual(result["status"], "EFFECTIVE_LIMITS_ALL_FOUR_PASS")
        self.assertEqual(len(called), 4)
        self.assertTrue(all(cmd[:2] == ("docker", "exec") for cmd in called))
        self.assertFalse(result["resource_sampling_during_batch"])
        names["client"] = "tcc2-v03-client"
        with self.assertRaises(ValueError):
            capture_effective_quotas("C2", names=names, query=query)

    def test_kube_new_namespace_only_with_valid_container_and_context(self):
        pods = {r: r+"-abcde" for r in
                ("attribute-source", "logic-engine", "rule-executor")}
        pods["client"] = "e11-benchmark-client"
        called = []
        def query(*argv):
            called.append(argv)
            role = "client" if "e11-benchmark-client" in argv else "service"
            return json.dumps(sample(CLIENT_MEMORY_BYTES if role == "client"
                                     else APP_MEMORY_BYTES))
        result = capture_effective_quotas(
            "C4", namespace="tcc2-pon-e11-c4-m01-b01",
            pods=pods, query=query)
        self.assertEqual(len(called), 4)
        self.assertEqual(result["status"], "EFFECTIVE_LIMITS_ALL_FOUR_PASS")
        self.assertTrue(all(cmd[0] == "kubectl" and
                            "--context" in cmd and
                            "-c" in cmd and
                            cmd[-3] == "python" and
                            cmd[-2] == "-c"
                            for cmd in called))
        with self.assertRaises(ValueError):
            capture_effective_quotas(
                "C4", namespace="tcc2-pon-c4", pods=pods, query=query)


if __name__ == "__main__":
    unittest.main()
