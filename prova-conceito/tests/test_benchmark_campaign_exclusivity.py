"""E11-M00C: testes puros do controle de uma bancada ativa, sem infraestrutura."""
import json
import unittest

from benchmark.campaign_exclusivity import check_exclusivity, check_exclusivity_readonly


class CampaignExclusivityTests(unittest.TestCase):
    def test_c2_without_new_campaign_and_with_old_pilots(self):
        result = check_exclusivity(
            "C2", "tcc2-pon-e11-c2-m01-b01",
            ["tcc2-pon-e11-c2-p20261115-232946-attribute-source",
             "tcc2-pon-worker", "tcc2-v03-logic-engine"],
            ["tcc2-pon", "tcc2-pon-c4"])
        self.assertEqual(result["status"], "ONE_NEW_CAMPAIGN_BENCH_ONLY")

    def test_another_running_new_c2_blocks(self):
        with self.assertRaises(ValueError):
            check_exclusivity(
                "C2", "tcc2-pon-e11-c2-m01-b02",
                ["tcc2-pon-e11-c2-m01-b01-attribute-source"], ["tcc2-pon"])

    def test_kube_target_only_allowed_old_namespace_safe(self):
        result = check_exclusivity(
            "C4", "tcc2-pon-e11-c4-m01-b01", [],
            ["tcc2-pon", "tcc2-pon-c4", "tcc2-pon-e11-c4-m01-b01"])
        self.assertEqual(result["new_kube_namespaces"],
                         ["tcc2-pon-e11-c4-m01-b01"])
        with self.assertRaises(ValueError):
            check_exclusivity(
                "C4", "tcc2-pon-e11-c4-m01-b01", [],
                ["tcc2-pon-e11-c4-m01-b01", "tcc2-pon-e11-c3-m01-b01"])

    def test_missing_target_fails(self):
        with self.assertRaises(ValueError):
            check_exclusivity("C3", "tcc2-pon-e11-c3-m01-b01", [], ["tcc2-pon"])

    def test_readonly_query_is_exact_and_does_not_mutate(self):
        calls = []
        def query(*argv):
            calls.append(argv)
            if argv[0] == "docker":
                return "tcc2-pon-worker\ntcc2-c2-attribute-source"
            return json.dumps({"items":[
                {"metadata":{"name":"tcc2-pon"}},
                {"metadata":{"name":"tcc2-pon-c4"}},
                {"metadata":{"name":"tcc2-pon-e11-c3-m01-b01"}}]})
        record = check_exclusivity_readonly(
            "C3", "tcc2-pon-e11-c3-m01-b01", query)
        self.assertEqual(record["scenario"], "C3")
        self.assertEqual(len(calls), 2)
        self.assertTrue(all("apply" not in cmd and "delete" not in cmd and
                            "rm" not in cmd for cmd in calls))


if __name__ == "__main__":
    unittest.main()
