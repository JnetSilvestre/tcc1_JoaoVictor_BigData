"""E11-M00: marcações/UID/ID de novos recursos; testes sem infraestrutura."""
import json
import unittest

from benchmark.ownership import capture_docker_ownership, capture_kind_ownership, exact_identity
from benchmark.prepare import render
from benchmark.docker_c2 import (
    build_client_command, build_service_command, ownership_label_args,
)


RUN = "e11-c2-m01-b01"
BASE = "tcc2-pon-e11-c2-m01-b01"
KUBE_RUN = "e11-c4-m01-b01"
KUBE_NS = "tcc2-pon-e11-c4-m01-b01"
LABELS = {"tcc2.e11/campaign": "m01", "tcc2.e11/run-id": RUN}


def docker_reader(tamper=None):
    net_id = "a" * 64
    info = {
        "Name": BASE, "Id": net_id, "Labels": LABELS.copy()
    }
    containers = {}
    for number, role in enumerate(("attribute-source", "logic-engine", "rule-executor", "client")):
        name = BASE + ("-benchmark-client" if role == "client" else "-" + role)
        containers[name] = {
            "Name": "/" + name, "Id": format(number + 1, "064x"),
            "Image": "sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a",
            "Config": {"Labels": LABELS.copy()},
            "State": {"Running": True},
            "NetworkSettings": {"Networks": {BASE: {"NetworkID": net_id}}},
        }
    if tamper is not None:
        tamper(info, containers)
    def query(*argv):
        if argv[:3] == ("docker", "network", "inspect"):
            assert argv[3] == BASE
            return json.dumps([info])
        assert argv[:2] == ("docker", "inspect")
        return json.dumps([containers[argv[2]]])
    return query


def kube_reader(tamper=None):
    labels = {"tcc2.e11/campaign": "m01", "tcc2.e11/run-id": KUBE_RUN}
    namespace = {"metadata": {"name": KUBE_NS, "uid": "new-namespace-uid", "labels": labels}}
    pods = []
    for number, role in enumerate(("attribute-source", "logic-engine", "rule-executor",
                                    "e11-benchmark-client")):
        name = role + ("-abcde" if role != "e11-benchmark-client" else "")
        pods.append({
            "metadata": {"namespace": KUBE_NS, "name": name, "uid": f"fresh-{number}",
                         "labels": {"app": role, "app.kubernetes.io/part-of": KUBE_NS}},
            "status": {"phase": "Running", "containerStatuses": [
                {"containerID": f"containerd://sha256:{number + 1:064x}",
                 "restartCount": 0}]},
        })
    if tamper is not None:
        tamper(namespace, pods)
    def query(*argv):
        assert argv[:3] == ("kubectl", "--context", "kind-tcc2-pon")
        if "namespace" in argv:
            return json.dumps(namespace)
        return json.dumps({"items": pods})
    return query


class OwnershipTests(unittest.TestCase):
    def test_new_run_id_and_historical_ids_are_not_interchangeable(self):
        self.assertEqual(exact_identity("C2", "m01-b01", RUN), BASE)
        with self.assertRaises(ValueError):
            exact_identity("C2", "p20261115-232946", "e11-c2-p20261115-232946")
        with self.assertRaises(ValueError):
            exact_identity("C3", "m01-b01", RUN)

    def test_docker_four_container_ids_and_network_id(self):
        record = capture_docker_ownership("m01-b01", RUN, docker_reader())
        self.assertEqual(record["status"], "NEW_BENCH_OWNERSHIP_READONLY_PASS")
        self.assertEqual(len(record["containers"]), 4)
        self.assertFalse(record["delete_authorized"])
        self.assertEqual(record["commands"], [])

    def test_docker_unmarked_or_wrong_image_rejected(self):
        def no_label(net, containers):
            net["Labels"]["tcc2.e11/run-id"] = "old-run"
        with self.assertRaises(ValueError):
            capture_docker_ownership("m01-b01", RUN, docker_reader(no_label))
        def image_changed(net, containers):
            containers[BASE+"-logic-engine"]["Image"] = "sha256:old"
        with self.assertRaises(ValueError):
            capture_docker_ownership("m01-b01", RUN, docker_reader(image_changed))

    def test_docker_duplicated_container_id_rejected(self):
        def duplicate(net, containers):
            containers[BASE+"-rule-executor"]["Id"] = containers[BASE+"-logic-engine"]["Id"]
        with self.assertRaises(ValueError):
            capture_docker_ownership("m01-b01", RUN, docker_reader(duplicate))

    def test_kind_four_pods_and_namespace_uid(self):
        record = capture_kind_ownership("C4", "m01-b01", KUBE_RUN, kube_reader())
        self.assertEqual(record["namespace"]["uid"], "new-namespace-uid")
        self.assertEqual(len(record["pods"]), 4)
        self.assertFalse(record["delete_authorized"])

    def test_kind_wrong_namespace_or_pod_uid_rejected(self):
        def changed_namespace(ns, pods):
            ns["metadata"]["labels"]["tcc2.e11/campaign"] = "pilot"
        with self.assertRaises(ValueError):
            capture_kind_ownership("C4", "m01-b01", KUBE_RUN, kube_reader(changed_namespace))
        def duplicate_pod_uid(ns, pods):
            pods[0]["metadata"]["uid"] = pods[1]["metadata"]["uid"]
        with self.assertRaises(ValueError):
            capture_kind_ownership("C4", "m01-b01", KUBE_RUN, kube_reader(duplicate_pod_uid))

    def test_kubernetes_render_tags_only_m_label(self):
        for scenario in ("C3", "C4"):
            with self.subTest(scenario=scenario):
                ns, yaml_text = render(scenario, "m01-b01")
                self.assertIn("tcc2.e11/campaign: m01", yaml_text)
                self.assertIn(f"tcc2.e11/run-id: e11-{scenario.lower()}-m01-b01", yaml_text)
                self.assertEqual(yaml_text.count("tcc2.e11/run-id:"), 1)
                self.assertIn(f"kind: Namespace\nmetadata:\n  name: {ns}", yaml_text)
                _, legacy = render(scenario, "p20261115")
                self.assertNotIn("tcc2.e11/run-id:", legacy)

    def test_docker_create_metadata_only_for_new_m(self):
        self.assertIn("--label", ownership_label_args(BASE))
        self.assertIn(f"tcc2.e11/run-id={RUN}", ownership_label_args(BASE))
        self.assertEqual(ownership_label_args("tcc2-pon-e11-c2-p20261115"), [])
        service = build_service_command("logic-engine", BASE+"-logic-engine", BASE)
        client = build_client_command(BASE+"-benchmark-client", BASE)
        self.assertIn(f"tcc2.e11/run-id={RUN}", service)
        self.assertIn(f"tcc2.e11/run-id={RUN}", client)


if __name__ == "__main__":
    unittest.main()
