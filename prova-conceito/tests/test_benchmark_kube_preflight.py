"""E11-D09: testes determinísticos de plano Kubernetes; sem Docker/Kubectl."""
import unittest
from benchmark.kube_preflight import (
    compare_snapshots, make_plans, summarize_kubelet,
    validate_manifest, verify_namespace_discovery, verify_nodes,
)
from benchmark.fixtures import generate


class KubernetesPlanReadOnlyTests(unittest.TestCase):
    def test_isolated_manifests_and_1000_oracle(self):
        rows=generate(1000,20260502,"e11-canonical-1000-20260502")
        plans=make_plans("p20261115-233000",rows)
        self.assertEqual(set(plans),{"C3","C4"})
        for scenario,plan in plans.items():
            self.assertEqual(plan["expected"]["requests"],1000)
            self.assertEqual(plan["expected"]["effects"],250)
            self.assertEqual(plan["checks"]["image_occurrences"],4)
            self.assertEqual(plan["checks"]["old_namespace_isolated"],True)
            self.assertIn("e11-benchmark-client",plan["manifest_text"])
            self.assertNotIn("namespace: tcc2-pon\n",plan["manifest_text"])
        self.assertIn("tcc2-pon-control-plane",
                      plans["C4"]["manifest_text"])

    def test_reject_historical_namespace_or_image(self):
        rows=generate(1000,20260502,"e11-canonical-1000-20260502")
        p=make_plans("p001",rows)["C3"]
        bad=p["manifest_text"].replace(
            f'namespace: {p["namespace"]}',"namespace: tcc2-pon",1)
        with self.assertRaises(ValueError):
            validate_manifest("C3",p["namespace"],bad)
        bad2=p["manifest_text"].replace(
            "image: tcc2-pon:c2-e08-dbefcd2cf3d2","image: unknown",1)
        with self.assertRaises(ValueError):
            validate_manifest("C3",p["namespace"],bad2)

    def test_namespace_discovery_rejects_existing_candidate(self):
        old=[{"metadata":{"name":x}} for x in ("tcc2-pon","tcc2-pon-c4")]
        self.assertEqual(len(verify_namespace_discovery(
            old,["tcc2-pon-e11-c3-p001"])["historic_present"]),2)
        with self.assertRaises(ValueError):
            verify_namespace_discovery(old+[{"metadata":{"name":"tcc2-pon-e11-c3-p001"}}],
                                       ["tcc2-pon-e11-c3-p001"])

    def test_node_ready_gate(self):
        items=[{"metadata":{"name":node,"uid":node},
                "status":{"conditions":[{"type":"Ready","status":"True"}],
                          "allocatable":{"cpu":"2","memory":"2048Mi"}}}
               for node in ("tcc2-pon-worker","tcc2-pon-control-plane")]
        self.assertEqual(len(verify_nodes(items)),2)
        items[0]["status"]["conditions"][0]["status"]="False"
        with self.assertRaises(ValueError):
            verify_nodes(items)

    def test_kubelet_fields_and_repeated_stamps(self):
        pod={"podRef":{"namespace":"tcc2-pon","name":"source","uid":"u1"},
             "containers":[{"name":"attribute-source",
                            "cpu":{"time":"2026-11-16T02:01:00Z",
                                   "usageCoreNanoSeconds":123},
                            "memory":{"time":"2026-11-16T02:01:00Z",
                                      "workingSetBytes":456}}]}
        first=summarize_kubelet({"pods":[pod]},"tcc2-pon-worker","read0")
        second=summarize_kubelet({"pods":[pod]},"tcc2-pon-worker","read1")
        self.assertEqual(first["cpu_fields_valid"],1)
        self.assertEqual(first["memory_fields_valid"],1)
        self.assertEqual(compare_snapshots(first,second)["cpu_timestamp_distinct"],0)
        pod["containers"][0]["cpu"]["time"]="2026-11-16T02:01:02Z"
        pod["containers"][0]["cpu"]["usageCoreNanoSeconds"]=125
        updated=summarize_kubelet({"pods":[pod]},"tcc2-pon-worker","read2")
        self.assertEqual(compare_snapshots(first,updated)["cpu_timestamp_distinct"],1)
        pod["containers"][0]["cpu"]["usageCoreNanoSeconds"]=0
        bad=summarize_kubelet({"pods":[pod]},"tcc2-pon-worker","read3")
        self.assertGreater(compare_snapshots(first,bad)["cpu_timestamp_regressions_or_counter_regressions"],0)


if __name__ == "__main__":
    unittest.main()
