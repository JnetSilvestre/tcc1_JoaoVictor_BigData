"""C2: testes puros, SEM Docker, sem contêineres, sem rede e sem POST."""
import unittest

from benchmark.docker_c2 import (
    CPU_LIMIT, IMAGE_TAG, MEM_APP, MEM_CLIENT, build_client_command,
    build_service_command, identities, validate_fixture,
)
from benchmark.fixtures import generate


class DockerPilotSafetyTests(unittest.TestCase):
    def test_isolated_names_and_canonical_fixture(self):
        rows = generate(100, 20260501, "e11-canonical-100-20260501")
        net, names = validate_fixture("p01", "e11-c2-p01", rows)
        self.assertEqual(net, "tcc2-pon-e11-c2-p01")
        self.assertEqual(len(set(names.values())), 4)
        self.assertNotIn("tcc2-c2-attribute-source", names.values())
        self.assertNotIn("tcc2-pon", names.values())
        with self.assertRaises(ValueError):
            validate_fixture("../old", "e11-c2-bad", rows)
        corrupted = [dict(x) for x in rows]
        corrupted[1]["value"] = 999
        with self.assertRaises(ValueError):
            validate_fixture("p02", "e11-c2-p02", corrupted)

    def test_service_arguments_and_limits(self):
        network, names = identities("p01")
        self.assertEqual(CPU_LIMIT, "0.5")
        for role in ("attribute-source", "logic-engine", "rule-executor"):
            cmd = build_service_command(role, names[role], network)
            self.assertEqual(cmd[0:3], ["docker", "run", "-d"])
            self.assertIn("--network-alias", cmd)
            self.assertEqual(cmd[cmd.index("--memory")+1], str(MEM_APP))
            self.assertEqual(cmd[cmd.index("--memory-swap")+1], str(MEM_APP))
            self.assertEqual(cmd[cmd.index("--cpus")+1], CPU_LIMIT)
            self.assertEqual(cmd[cmd.index("--network")+1], network)
            self.assertEqual(cmd[cmd.index("--network-alias")+1], role)
            self.assertIn(IMAGE_TAG, cmd)
            self.assertNotIn("-p", cmd)
        self.assertIn("logic-engine", build_service_command(
            "attribute-source", names["attribute-source"], network))
        self.assertIn("rule-executor", build_service_command(
            "logic-engine", names["logic-engine"], network))
        self.assertNotIn("--downstream-port", build_service_command(
            "rule-executor", names["rule-executor"], network))

    def test_client_uses_same_image_but_different_entrypoint(self):
        network, names = identities("p01")
        cmd = build_client_command(names["client"], network)
        self.assertEqual(cmd[cmd.index("--entrypoint")+1], "python")
        self.assertEqual(cmd[cmd.index("--memory")+1], str(MEM_CLIENT))
        self.assertIn(IMAGE_TAG, cmd)
        self.assertEqual(cmd[-3], IMAGE_TAG)
        self.assertEqual(cmd[-2], "-c")
        self.assertIn("time.sleep(86400)", cmd[-1])


if __name__ == "__main__":
    unittest.main()
