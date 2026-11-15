"""Testes locais do preflight V03 frio, sem Docker e sem alterar os serviços."""
import copy
import unittest

from c1.state import AttributeSource, LogicEngine, RuleExecutor
from c2.v03_cold import assert_cold


class V03ColdPreflightTests(unittest.TestCase):
    def setUp(self):
        noop = lambda event: None
        self.states = {
            "attribute-source": AttributeSource(noop, noop).state(),
            "logic-engine": LogicEngine(noop, noop).state(),
            "rule-executor": RuleExecutor().state(),
        }

    def test_real_cold_state_from_implementations_accepted(self):
        self.assertIsNone(self.states["logic-engine"]["attributes"])
        self.assertIsNone(self.states["logic-engine"]["condition"])
        self.assertIsNone(self.states["rule-executor"]["approved"])
        assert_cold(self.states)

    def test_rejects_logic_engine_attributes_materialized_too_early(self):
        modified = copy.deepcopy(self.states)
        modified["logic-engine"]["attributes"] = {"atA": 0, "atB": 0}
        with self.assertRaisesRegex(ValueError, "logic-engine frio"):
            assert_cold(modified)

    def test_rejects_attribute_sequence_different_from_zero(self):
        modified = copy.deepcopy(self.states)
        modified["logic-engine"]["sequences"]["atB"] = 1
        with self.assertRaisesRegex(ValueError, "sequencias alteradas"):
            assert_cold(modified)

    def test_rejects_already_initialized_source(self):
        modified = copy.deepcopy(self.states)
        modified["attribute-source"]["run_id"] = "v03-test"
        modified["attribute-source"]["ready"] = True
        with self.assertRaisesRegex(ValueError, "ja foi inicializada"):
            assert_cold(modified)

    def test_rejects_executor_approved_before_snapshot(self):
        modified = copy.deepcopy(self.states)
        modified["rule-executor"]["approved"] = False
        with self.assertRaisesRegex(ValueError, "executor contem historico"):
            assert_cold(modified)


if __name__ == "__main__":
    unittest.main()
