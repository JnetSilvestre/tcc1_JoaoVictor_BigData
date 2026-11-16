"""E11-M00C: testes puros do preflight final; sem Docker, kubectl ou POST."""
import unittest

from benchmark.campaign_controls import ROLES, validate_cold, final_readonly_cold_check
from c1.state import AttributeSource, LogicEngine, RuleExecutor


def fixtures():
    attrs = {"atA": 0, "atB": 0}
    states = {
        "attribute-source": {
            "ready": False, "run_id": None, "attributes": attrs.copy(),
            "sequences": attrs.copy(), "pending_request_id": None,
        },
        "logic-engine": {
            "ready": False, "run_id": None, "attributes": None,
            "sequences": attrs.copy(), "condition": None,
            "condition_sequence": 0, "received_ids": [],
            "condition_events": [], "faulted": False,
        },
        "rule-executor": {
            "ready": False, "run_id": None, "approved": None,
            "condition_sequence": 0, "received_ids": [],
            "effects": [], "faulted": False,
        },
    }
    return {r: {"live": True} for r in ROLES}, states, {r: [] for r in ROLES}


class UniformColdCheckTests(unittest.TestCase):
    def test_canonical_cold_state(self):
        live, states, logs = fixtures()
        result = validate_cold(live, states, logs)
        self.assertEqual(result["status"], "PASS_COLD_READ_ONLY")
        self.assertEqual(result["mutation_count"], 0)
        self.assertEqual(result["functional_warmup_posts"], 0)

    def test_exactly_one_final_get_and_log_per_role(self):
        live, states, logs = fixtures()
        calls = []
        def health(role):
            calls.append((role, "health"))
            return live[role]
        def state(role):
            calls.append((role, "state"))
            return states[role]
        def read_logs(role):
            calls.append((role, "logs"))
            return logs[role]
        out = final_readonly_cold_check(health, state, read_logs)
        self.assertEqual(len(calls), 9)
        self.assertEqual(
            calls,
            [(r, method) for r in ROLES for method in ("health", "state", "logs")])
        self.assertTrue(out["pre_snapshot"])
        self.assertTrue(out["started_utc"] <= out["ended_utc"])

    def test_fail_if_health_unready_or_missing_role(self):
        live, states, logs = fixtures()
        live["logic-engine"]["live"] = False
        with self.assertRaises(ValueError):
            validate_cold(live, states, logs)
        live, states, logs = fixtures()
        del states["rule-executor"]
        with self.assertRaises(ValueError):
            validate_cold(live, states, logs)

    def test_fail_on_old_or_changed_state(self):
        live, states, logs = fixtures()
        states["attribute-source"]["ready"] = True
        with self.assertRaises(ValueError):
            validate_cold(live, states, logs)
        live, states, logs = fixtures()
        states["logic-engine"]["attributes"] = {"atA": 0, "atB": 1}
        with self.assertRaises(ValueError):
            validate_cold(live, states, logs)
        live, states, logs = fixtures()
        states["attribute-source"]["sequences"]["atA"] = 1
        with self.assertRaises(ValueError):
            validate_cold(live, states, logs)

    def test_actual_uninitialized_states_are_not_falsely_rejected(self):
        live, states, logs = fixtures()
        self.assertIsNone(states["logic-engine"]["attributes"])
        self.assertIsNone(states["logic-engine"]["condition"])
        self.assertIsNone(states["rule-executor"]["approved"])
        self.assertEqual(validate_cold(live, states, logs)["status"],
                         "PASS_COLD_READ_ONLY")
        states["logic-engine"]["condition"] = False
        with self.assertRaises(ValueError):
            validate_cold(live, states, logs)
        live, states, logs = fixtures()
        states["rule-executor"]["approved"] = False
        with self.assertRaises(ValueError):
            validate_cold(live, states, logs)

    def test_contract_using_real_c1_state_classes_no_network(self):
        source = AttributeSource(lambda _x: None, lambda _x: None)
        logic = LogicEngine(lambda _x: None, lambda _x: None)
        executor = RuleExecutor()
        states = {
            "attribute-source": source.state(),
            "logic-engine": logic.state(),
            "rule-executor": executor.state(),
        }
        live = {r: {"live": True} for r in ROLES}
        logs = {r: [] for r in ROLES}
        self.assertEqual(
            validate_cold(live, states, logs)["status"], "PASS_COLD_READ_ONLY")

    def test_reject_ledger_effects_pending_and_logs(self):
        for role, key, value in (
            ("attribute-source", "pending_request_id", "old"),
            ("logic-engine", "condition_events", [{"event": 1}]),
            ("logic-engine", "received_ids", ["old"]),
            ("rule-executor", "effects", ["old"]),
            ("rule-executor", "approved", True),
        ):
            with self.subTest(role=role, field=key):
                live, states, logs = fixtures()
                states[role][key] = value
                with self.assertRaises(ValueError):
                    validate_cold(live, states, logs)
        live, states, logs = fixtures()
        logs["rule-executor"].append({"event_type": "mutation"})
        with self.assertRaises(ValueError):
            validate_cold(live, states, logs)


if __name__ == "__main__":
    unittest.main()
