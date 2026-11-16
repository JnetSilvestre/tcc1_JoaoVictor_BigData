"""Testes E11: sintese deterministica, sem Kubernetes, Docker ou HTTP real."""
import unittest

from benchmark.collector import parse_summary, quality
from benchmark.evidence import check_run
from benchmark.fixtures import characterize, generate, rebase
from benchmark.prepare import render, namespace_for
from benchmark.runner import ensure_safe
from c0.io import validate_input
from c0.oracle import calculate_expected_effects


class FixtureTests(unittest.TestCase):
    def test_reproducibility(self):
        for n, seed in ((100, 20260501), (1000, 20260502), (10000, 20260503)):
            run_id = f"e11-canonical-{n}-{seed}"
            first = generate(n, seed, run_id)
            self.assertEqual(first, generate(n, seed, run_id))
            self.assertEqual(len(first), n)
            self.assertEqual(validate_input(first), (run_id, seed))

    def test_eight_step_cycle(self):
        rows = generate(8, 20260501, "e11-test")
        self.assertEqual([r["step"] for r in calculate_expected_effects(rows)], [3, 7])
        counts = characterize(rows)
        self.assertEqual(counts["changed"], 6)
        self.assertEqual(counts["condition_transitions"], 4)

    def test_rebase_and_namespace_guard(self):
        rows = generate(100, 20260501, "e11-canonical-100-20260501")
        rebased = rebase(rows, "e11-c3-p01")
        self.assertEqual(len(calculate_expected_effects(rows)),
                         len(calculate_expected_effects(rebased)))
        self.assertEqual(ensure_safe("C3", "p01", "e11-c3-p01", rows),
                         "tcc2-pon-e11-c3-p01")
        with self.assertRaises(ValueError):
            ensure_safe("C4", "p01", "c4-e10-i02-v1", rows)
        corrupted = [dict(x) for x in rows]
        corrupted[1]["value"] = 99
        with self.assertRaises(ValueError):
            ensure_safe("C3", "p02", "e11-c3-p02", corrupted)

    def test_manifests_do_not_target_original_namespaces(self):
        for scenario in ("C3", "C4"):
            ns, content = render(scenario, "p01")
            self.assertEqual(ns, namespace_for(scenario, "p01"))
            self.assertIn(f"namespace: {ns}", content)
            self.assertIn("name: e11-benchmark-client", content)
            self.assertIn("image: tcc2-pon:c2-e08-dbefcd2cf3d2", content)
            self.assertNotIn("  namespace: tcc2-pon\n", content)
            self.assertNotIn("  namespace: tcc2-pon-c4\n", content)
        with self.assertRaises(ValueError):
            namespace_for("C3", "../tcc2-pon")


class CollectorTests(unittest.TestCase):
    def test_cpu_memory_and_pod_network_paths(self):
        sample = {"pods": [{
            "podRef": {"name": "s", "namespace": "tcc2-pon-e11-c3-p01", "uid": "xyz"},
            "containers": [{"name": "attribute-source",
                            "cpu": {"time": "2026-11-15T23:00:00Z",
                                    "usageCoreNanoSeconds": 12},
                            "memory": {"time": "2026-11-15T23:00:00Z",
                                       "workingSetBytes": 4096}}],
            "network": {"rxBytes": 14, "txBytes": 28, "interfaces": [{"name": "eth0"}]},
        }]}
        rows = parse_summary(sample, "tcc2-pon-e11-c3-p01", "worker", "utc", 0.1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["cpu_usage_core_ns"], 12)
        self.assertEqual(rows[0]["memory_working_set_bytes"], 4096)
        self.assertEqual(rows[0]["network_rx_bytes_pod"], 14)
        self.assertFalse(quality(rows, {"source": ("xyz", "attribute-source")})["usable_cpu"])


class ValidationTests(unittest.TestCase):
    def test_http_and_oracle_checks_detect_divergence(self):
        rows = generate(8, 20260501, "e11-test")
        values, seq = {"atA": 0, "atB": 0}, {"atA": 0, "atB": 0}
        condition, count_conditions = False, 0
        results = []
        for row in rows:
            name = row["entity_id"]
            changed = values[name] != row["value"]
            if changed:
                values[name] = row["value"]
                seq[name] += 1
                approved = values["atA"] >= 5 and values["atB"] == 1
                if condition != approved:
                    condition, count_conditions = approved, count_conditions + 1
            event_id = f"e11-test:{name}:{seq[name]}" if changed else None
            results.append({"type": "request", "step": row["step"], "status": 200,
                            "response": {"changed": changed, "sequence": seq[name],
                                         "event_id": event_id,
                                         "duplicate_request": False}})
        results.append({"type": "summary", "status": "PASS",
                        "requests_sent": 8, "elapsed_ns": 10000})
        states = {
            "attribute-source": {"ready": True, "attributes": values,
                                 "sequences": seq, "pending_request_id": None},
            "logic-engine": {"ready": True, "attributes": values, "sequences": seq,
                             "condition_sequence": count_conditions,
                             "condition": condition,
                             "received_ids": list(range(sum(seq.values()))),
                             "faulted": False},
            "rule-executor": {"ready": True, "condition_sequence": count_conditions,
                              "approved": condition, "effects": calculate_expected_effects(rows),
                              "received_ids": list(range(count_conditions)),
                              "faulted": False},
        }
        self.assertEqual(check_run(rows, results, states)["status"], "PASS")
        results[2]["response"]["changed"] = False
        self.assertEqual(check_run(rows, results, states)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
