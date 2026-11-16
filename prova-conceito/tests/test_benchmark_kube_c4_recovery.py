"""E11-R01: testes dos gates de recuperacao C4; sem kubectl ou POST."""
import unittest
from benchmark.kube_c4_recovery import (
    check_cold_complete, check_historical, check_pod_stability,
    EXPECTED_NODES, KNOWN_NS, IMAGE
)


def fake_pod(role, index):
    return {
        "metadata":{"labels":{"app":role}, "name":f"pod-{index}",
                    "namespace":KNOWN_NS,"uid":f"uid-{index}"},
        "spec":{"nodeName":EXPECTED_NODES[role],
                "containers":[{"image":IMAGE}]},
        "status":{"phase":"Running",
                  "containerStatuses":[{
                      "ready":True,"restartCount":0,
                      "containerID":f"containerd://id-{index}",
                      "imageID":"sha256:approved"}]},
    }


class KubeC4RecoveryTests(unittest.TestCase):
    def make_pods(self):
        return {"items":[fake_pod(role,i) for i,role in enumerate(EXPECTED_NODES)]}

    def make_states(self):
        return {
            "attribute-source":{"ready":False,"run_id":None,"snapshot_version":None,
                "attributes":{"atA":0,"atB":0},"sequences":{"atA":0,"atB":0},
                "pending_request_id":None,"faulted":False},
            "logic-engine":{"ready":False,"run_id":None,"snapshot_version":None,
                "attributes":None,"sequences":{"atA":0,"atB":0},
                "condition":None,"condition_sequence":0,
                "received_ids":[],"condition_events":[],"faulted":False},
            "rule-executor":{"ready":False,"run_id":None,"snapshot_version":None,
                "approved":None,"condition_sequence":0,
                "received_ids":[],"effects":[],"faulted":False},
        }

    def test_stable_four_pods(self):
        p=self.make_pods()
        self.assertEqual(len(check_pod_stability(p,p)),4)

    def test_changed_uid_or_restart_is_blocked(self):
        p=self.make_pods()
        q=self.make_pods()
        q["items"][0]["metadata"]["uid"]="unexpected-uid"
        with self.assertRaises(ValueError):
            check_pod_stability(p,q)
        q=self.make_pods()
        q["items"][1]["status"]["containerStatuses"][0]["restartCount"]=1
        with self.assertRaises(ValueError):
            check_pod_stability(p,q)

    def test_snapshot_must_not_exist(self):
        states=self.make_states()
        self.assertTrue(check_cold_complete(states))
        states["attribute-source"]["run_id"]="old-run"
        with self.assertRaises(ValueError):
            check_cold_complete(states)
        states=self.make_states()
        states["logic-engine"]["condition_sequence"]=1
        with self.assertRaises(ValueError):
            check_cold_complete(states)

    def test_historical_pods_unchanged(self):
        n=("tcc2-pon", "tcc2-pon-c4", "tcc2-pon-e11-c3-p20261115-235728")
        before={x:["p:uid"] for x in n}
        self.assertTrue(check_historical(before,before))
        after={**before,"tcc2-pon-c4":["q:uid"]}
        with self.assertRaises(ValueError):
            check_historical(before,after)

    def test_no_extra_or_missing_pods(self):
        p=self.make_pods()
        q=self.make_pods()
        q["items"].append(fake_pod("logic-engine",9))
        with self.assertRaises(ValueError):
            check_pod_stability(p,q)


if __name__=="__main__":
    unittest.main()
