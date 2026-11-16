"""E11-M00B: testes sinteticos do contrato de recursos, sem Kubernetes real."""
import unittest

from benchmark.resource_contract import verify_kube_resources


def container(req_memory, lim_memory):
    return {"resources": {
        "requests": {"cpu": "100m", "memory": req_memory},
        "limits": {"cpu": "500m", "memory": lim_memory},
    }}


def topology():
    roles = ("attribute-source", "logic-engine", "rule-executor")
    pods = [{"metadata": {"labels": {"app": role}},
             "spec": {"containers": [container("128Mi", "256Mi")]}}
            for role in roles]
    deploys = [{"metadata": {"name": role},
                "spec": {"template": {"spec": {"containers": [
                    container("128Mi", "256Mi")]}}}}
               for role in roles]
    client = {"spec": {"containers": [container("64Mi", "128Mi")]}}
    return {"pods_full": {"items": pods},
            "deployments_full": {"items": deploys}}, client


class ResourceContractTests(unittest.TestCase):
    def test_declared_quota_passes_but_not_physical_equivalence(self):
        data, client = topology()
        result = verify_kube_resources(data, client)
        self.assertEqual(result["status"], "DECLARED_LIMITS_MATCH")
        self.assertFalse(result["physical_cpu_memory_equivalence"])
        self.assertEqual(set(result["services"]),
                         {"attribute-source", "logic-engine", "rule-executor"})

    def test_changed_cpu_limit_is_blocked(self):
        data, client = topology()
        data["pods_full"]["items"][0]["spec"]["containers"][0]["resources"]["limits"]["cpu"] = "1"
        with self.assertRaises(ValueError):
            verify_kube_resources(data, client)

    def test_missing_request_is_blocked(self):
        data, client = topology()
        del data["deployments_full"]["items"][0]["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]
        with self.assertRaises(ValueError):
            verify_kube_resources(data, client)

    def test_client_limit_is_checked(self):
        data, client = topology()
        client["spec"]["containers"][0]["resources"]["limits"]["memory"] = "256Mi"
        with self.assertRaises(ValueError):
            verify_kube_resources(data, client)

    def test_missing_pods_block(self):
        data, client = topology()
        data["pods_full"]["items"].pop()
        with self.assertRaises(ValueError):
            verify_kube_resources(data, client)


if __name__ == "__main__":
    unittest.main()
