"""E11-M00F: executador de C2-S01 exercitado apenas em runtime sintetico."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from benchmark.retirement_execute_c2_s01 import (
    APPROVAL, BASE, CONTAINER_IDS, IMAGE_ID, JOURNAL_NAME,
    NETWORK_ID, RUN_ID, STOP_ORDER, ZIP_SHA256,
    execute_only_s01, expected_name, inspect_target, validate_frozen_plan,
)


HEAD = "b" * 40
LABELS = {
    "tcc2.e11/campaign": "m01", "tcc2.e11/run-id": RUN_ID,
}


def frozen_plan():
    return {
        "status": "RETIREMENT_PREVIEW_READONLY_PASS_NOT_AUTHORIZATION",
        "scenario": "C2", "run_id": RUN_ID, "zip_sha256": ZIP_SHA256,
        "backup_sha256": ZIP_SHA256,
        "expected_new_resource_names": {
            "network": BASE,
            "containers": [expected_name(role) for role in (
                "attribute-source", "logic-engine", "rule-executor", "client")],
        },
        "resource_immutable_ids": {
            "network_id": NETWORK_ID, "container_ids": dict(CONTAINER_IDS),
        },
        "historic_resources_mutated": False,
        "inventory": {"containers": 4, "networks": 1,
                      "new_kube_namespaces": 0, "unexpected_new_resources": 0},
        "requires_explicit_operator_approval": True,
        "requires_tested_execution_procedure": True,
        "delete_authorized": False, "commands": [],
    }


class FakeRuntime:
    """Nenhum comando docker executado: so altera estruturas em memoria."""
    def __init__(self):
        self.running = {id_: True for id_ in CONTAINER_IDS.values()}
        self.present = set(CONTAINER_IDS.values())
        self.network_present = True
        self.actions = []
        self.foreign_network = False
        self.label_tamper = False
        self.fail_action = None

    def query(self, *args):
        if args[:3] == ("docker", "container", "inspect"):
            identifier = args[3]
            if identifier not in self.present:
                raise ValueError("container sintético removido")
            role = next(r for r in CONTAINER_IDS
                        if CONTAINER_IDS[r] == identifier)
            labels = dict(LABELS)
            if self.label_tamper and role == "logic-engine":
                labels["tcc2.e11/run-id"] = "historic"
            nets = {BASE: {"NetworkID": NETWORK_ID}}
            if self.foreign_network:
                nets["bridge"] = {"NetworkID": "x" * 64}
            return json.dumps([{
                "Id": identifier, "Name": "/" + expected_name(role),
                "Image": IMAGE_ID, "Config": {"Labels": labels},
                "State": {"Running": self.running[identifier]},
                "NetworkSettings": {"Networks": nets},
            }])
        if args == ("docker", "network", "inspect", NETWORK_ID):
            if not self.network_present:
                raise ValueError("rede sintetica removida")
            return json.dumps([{
                "Id": NETWORK_ID, "Name": BASE, "Labels": dict(LABELS),
                "Containers": {identifier: {"Name": expected_name(role)}
                               for role, identifier in CONTAINER_IDS.items()
                               if identifier in self.present and self.running[identifier]},
            }])
        if args == ("docker", "ps", "-a", "--format", "{{.Names}}"):
            return "\n".join(
                expected_name(role) for role, identifier in CONTAINER_IDS.items()
                if identifier in self.present) + "\ntcc2-v06-attribute-source"
        if args == ("docker", "network", "ls", "--format", "{{.Name}}"):
            return "bridge\nkind\n" + (BASE if self.network_present else "") + "\ntcc2-pon-c2"
        raise AssertionError(f"consulta nao prevista: {args!r}")

    def action(self, *args):
        self.actions.append(args)
        if self.fail_action == len(self.actions):
            raise RuntimeError("falha simulada na mutacao")
        if args[:4] == ("docker", "container", "stop", "--time"):
            if len(args) != 6 or args[4] != "10" or args[5] not in self.present:
                raise AssertionError("stop fora da allowlist")
            if not self.running[args[5]]:
                raise AssertionError("stop repetido")
            self.running[args[5]] = False
        elif args[:3] == ("docker", "container", "rm"):
            if len(args) != 4 or args[3] not in self.present:
                raise AssertionError("rm fora da allowlist")
            if self.running[args[3]]:
                raise AssertionError("rm de container ativo")
            self.present.remove(args[3])
        elif args[:3] == ("docker", "network", "rm"):
            if len(args) != 4 or args[3] != NETWORK_ID or self.present:
                raise AssertionError("network rm nao autorizado")
            self.network_present = False
        else:
            raise AssertionError("comando mutante diferente do aprovado")


class C2S01RetirementExecutorTests(unittest.TestCase):
    def test_exact_plan_has_expected_frozen_allowlist(self):
        validate_frozen_plan(frozen_plan())
        self.assertEqual(len(CONTAINER_IDS), 4)

    def test_wrong_id_and_wrong_sha_block(self):
        altered = frozen_plan()
        altered["resource_immutable_ids"]["container_ids"]["client"] = "f" * 64
        with self.assertRaises(ValueError):
            validate_frozen_plan(altered)
        altered = frozen_plan()
        altered["zip_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            validate_frozen_plan(altered)

    def test_foreign_scenario_and_extra_new_resources_block(self):
        altered = frozen_plan()
        altered["scenario"] = "C3"
        with self.assertRaises(ValueError):
            validate_frozen_plan(altered)
        altered = frozen_plan()
        altered["inventory"]["unexpected_new_resources"] = 1
        with self.assertRaises(ValueError):
            validate_frozen_plan(altered)

    def test_wrong_consent_blocks_before_journal_or_actions(self):
        runtime = FakeRuntime()
        with TemporaryDirectory() as tmp:
            journal = Path(tmp) / JOURNAL_NAME
            with self.assertRaises(ValueError):
                execute_only_s01(frozen_plan(), runtime.query, runtime.action,
                                 journal, "nao_autorizado", HEAD, HEAD)
            self.assertFalse(journal.exists())
            self.assertEqual(runtime.actions, [])

    def test_wrong_git_sha_blocks_before_journal_or_actions(self):
        runtime = FakeRuntime()
        with TemporaryDirectory() as tmp:
            journal = Path(tmp) / JOURNAL_NAME
            with self.assertRaises(ValueError):
                execute_only_s01(frozen_plan(), runtime.query, runtime.action,
                                 journal, APPROVAL, "a" * 40, HEAD)
            self.assertFalse(journal.exists())
            self.assertEqual(runtime.actions, [])

    def test_wrong_labels_fail_before_first_mutation(self):
        runtime = FakeRuntime()
        runtime.label_tamper = True
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                execute_only_s01(frozen_plan(), runtime.query, runtime.action,
                                 Path(tmp) / JOURNAL_NAME, APPROVAL, HEAD, HEAD)
        self.assertFalse(runtime.actions)

    def test_extra_network_attachment_fail_before_first_mutation(self):
        runtime = FakeRuntime()
        runtime.foreign_network = True
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                execute_only_s01(frozen_plan(), runtime.query, runtime.action,
                                 Path(tmp) / JOURNAL_NAME, APPROVAL, HEAD, HEAD)
        self.assertFalse(runtime.actions)

    def test_complete_simulated_retirement_is_exact_and_journaled(self):
        runtime = FakeRuntime()
        with TemporaryDirectory() as tmp:
            journal = Path(tmp) / JOURNAL_NAME
            result = execute_only_s01(frozen_plan(), runtime.query, runtime.action,
                                      journal, APPROVAL, HEAD, HEAD)
            self.assertEqual(result["status"], "S01_RETIREMENT_COMPLETE")
            self.assertEqual(len(runtime.actions), 9)
            self.assertEqual([x[-1] for x in runtime.actions[:4]],
                             [CONTAINER_IDS[r] for r in STOP_ORDER])
            self.assertEqual([x[-1] for x in runtime.actions[4:8]],
                             [CONTAINER_IDS[r] for r in STOP_ORDER])
            self.assertEqual(runtime.actions[-1], ("docker", "network", "rm", NETWORK_ID))
            self.assertFalse(runtime.present)
            self.assertFalse(runtime.network_present)
            lines = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(lines[0]["stage"], "AUTHORIZED_BEGIN")
            self.assertEqual(lines[-1]["stage"], "COMPLETE")
            self.assertEqual(len([x for x in lines if x["stage"] == "BEFORE_STOP"]), 4)
            self.assertEqual(len([x for x in lines if x["stage"] == "BEFORE_RM"]), 4)

    def test_failure_journals_and_never_retries(self):
        runtime = FakeRuntime()
        runtime.fail_action = 2
        with TemporaryDirectory() as tmp:
            journal = Path(tmp) / JOURNAL_NAME
            with self.assertRaises(RuntimeError):
                execute_only_s01(frozen_plan(), runtime.query, runtime.action,
                                 journal, APPROVAL, HEAD, HEAD)
            lines = [json.loads(x) for x in journal.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(lines[-1]["stage"], "INTERRUPTED_DO_NOT_RETRY")
            self.assertEqual(len(runtime.actions), 2)
            with self.assertRaises((ValueError, FileExistsError)):
                execute_only_s01(frozen_plan(), runtime.query, runtime.action,
                                 journal, APPROVAL, HEAD, HEAD)
            self.assertEqual(len(runtime.actions), 2)

    def test_existing_journal_blocks_before_mutation(self):
        runtime = FakeRuntime()
        with TemporaryDirectory() as tmp:
            journal = Path(tmp) / JOURNAL_NAME
            journal.write_text("previous run", encoding="utf-8")
            with self.assertRaises(ValueError):
                execute_only_s01(frozen_plan(), runtime.query, runtime.action,
                                 journal, APPROVAL, HEAD, HEAD)
            self.assertEqual(runtime.actions, [])


if __name__ == "__main__":
    unittest.main()
