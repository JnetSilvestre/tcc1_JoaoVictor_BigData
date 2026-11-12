"""Regressões C1 de estado em memória; NÃO são testes HTTP/multiprocesso."""

import copy
import unittest

from c0.io import read_jsonl
from c1.protocol import ContractError, utc_now
from c1.state import AttributeSource, LogicEngine, RuleExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "c0_minimo.jsonl"
EXPECTED = ROOT / "fixtures" / "c0_esperado.jsonl"


class C1StateTests(unittest.TestCase):
    def setUp(self):
        self.rows = read_jsonl(FIXTURE)
        self.expected = read_jsonl(EXPECTED)
        self.executor = RuleExecutor()
        self.engine = LogicEngine(
            self.executor.initialize, self.executor.receive
        )
        self.sent_attributes = []

        def send_attribute(event):
            self.sent_attributes.append(dict(event))
            return self.engine.receive(event)

        self.source = AttributeSource(self.engine.initialize, send_attribute)

    def initialize(self):
        return self.source.initialize(self.rows[0]["run_id"])

    def process_rows(self):
        self.initialize()
        return [self.source.change(row) for row in self.rows]

    def test_snapshot_before_events_and_three_states_ready(self):
        with self.assertRaises(ContractError):
            self.source.change(self.rows[0])
        with self.assertRaises(ContractError):
            self.engine.receive({
                "schema_version": 1, "event_id": "r:atA:1",
                "run_id": "r", "source": "attribute-source",
                "entity_id": "atA", "sequence": 1, "value": 5,
                "emitted_at": utc_now(),
            })
        with self.assertRaises(ContractError):
            self.executor.receive({
                "schema_version": 1, "event_id": "r:cn1:1",
                "run_id": "r", "source": "logic-engine",
                "entity_id": "cn1", "sequence": 1, "approved": True,
                "caused_by": "r:atB:1", "emitted_at": utc_now(),
            })
        self.assertFalse(self.engine.ready)
        self.assertFalse(self.executor.ready)
        result = self.initialize()
        self.assertTrue(result["ready"])
        self.assertTrue(all((
            self.source.ready, self.engine.ready, self.executor.ready,
        )))
        self.assertEqual(self.engine.state()["snapshot_version"], result["snapshot_version"])
        self.assertEqual(self.executor.state()["snapshot_version"], result["snapshot_version"])

    def test_same_snapshot_idempotent_conflicting_snapshot_rejected(self):
        self.initialize()
        snapshot = {
            "schema_version": 1, "run_id": self.rows[0]["run_id"],
            "snapshot_version": self.source.snapshot_version,
            "attributes": {"atA": 0, "atB": 0},
            "sequences": {"atA": 0, "atB": 0},
        }
        self.assertTrue(self.engine.initialize(snapshot)["duplicate"])
        self.assertTrue(self.source.initialize(self.rows[0]["run_id"])["duplicate"])
        with self.assertRaises(ContractError):
            self.engine.initialize({
                **snapshot, "attributes": {"atA": 5, "atB": 0},
            })
        self.assertEqual(self.engine.state()["attributes"], {"atA": 0, "atB": 0})

    def test_output_equals_independent_c0_fixture(self):
        responses = self.process_rows()
        self.assertEqual([r["changed"] for r in responses], [
            False, True, True, False, True, True, True,
        ])
        self.assertEqual(self.executor.state()["effects"], self.expected)
        self.assertEqual(len(self.sent_attributes), 5)
        self.assertEqual(len(self.engine.condition_events), 3)
        self.assertEqual(self.source.state()["sequences"], {"atA": 2, "atB": 3})
        self.assertEqual(self.engine.state()["sequences"], {"atA": 2, "atB": 3})
        self.assertEqual(self.executor.state()["condition_sequence"], 3)

    def test_repeated_change_request_does_not_duplicate_events(self):
        self.initialize()
        change = self.rows[1]
        first = self.source.change(change)
        second = self.source.change(change)
        self.assertFalse(first["duplicate_request"])
        self.assertTrue(second["duplicate_request"])
        self.assertEqual(first["event_id"], second["event_id"])
        self.assertEqual(len(self.sent_attributes), 1)
        self.assertEqual(self.engine.state()["sequences"]["atA"], 1)
        with self.assertRaises(ContractError):
            self.source.change({**change, "value": 99})

    def test_replay_attribute_and_condition_events_is_idempotent(self):
        self.process_rows()
        original_effects = copy.deepcopy(self.executor.effects)
        first_attribute = self.sent_attributes[0]
        condition = self.engine.condition_events[0]
        self.assertTrue(self.engine.receive(first_attribute)["duplicate"])
        self.assertTrue(self.executor.receive(condition)["duplicate"])
        self.assertEqual(self.executor.effects, original_effects)

    def test_duplicated_event_id_with_different_body_is_rejected(self):
        self.process_rows()
        before = copy.deepcopy(self.engine.state())
        first = self.sent_attributes[0]
        with self.assertRaises(ContractError):
            self.engine.receive({**first, "value": 999})
        self.assertEqual(self.engine.state(), before)
        condition = self.engine.condition_events[0]
        before_executor = copy.deepcopy(self.executor.state())
        with self.assertRaises(ContractError):
            self.executor.receive({**condition, "step": 999})
        self.assertEqual(self.executor.state(), before_executor)

    def test_gap_and_wrong_run_are_blocked_without_mutation(self):
        self.initialize()
        before = copy.deepcopy(self.engine.state())
        gap = {
            "schema_version": 1,
            "event_id": f"{self.source.run_id}:atA:2",
            "run_id": self.source.run_id, "source": "attribute-source",
            "entity_id": "atA", "sequence": 2, "value": 5,
            "emitted_at": utc_now(),
        }
        with self.assertRaises(ContractError):
            self.engine.receive(gap)
        with self.assertRaises(ContractError):
            self.engine.receive({
                **gap, "run_id": "wrong-run",
                "event_id": "wrong-run:atA:2",
            })
        self.assertEqual(self.engine.state(), before)

    def test_executor_sequence_gap_without_effect(self):
        self.initialize()
        before = copy.deepcopy(self.executor.state())
        event = {
            "schema_version": 1,
            "event_id": f"{self.source.run_id}:cn1:2",
            "run_id": self.source.run_id, "source": "logic-engine",
            "entity_id": "cn1", "sequence": 2, "approved": True,
            "caused_by": f"{self.source.run_id}:atB:1",
            "emitted_at": utc_now(),
        }
        with self.assertRaises(ContractError):
            self.executor.receive(event)
        self.assertEqual(self.executor.state(), before)

    def test_invalid_attribute_payload_does_not_mutate_state(self):
        self.initialize()
        before = copy.deepcopy(self.source.state())
        with self.assertRaises(ContractError):
            self.source.change({**self.rows[1], "value": True})
        self.assertEqual(self.source.state(), before)

    def test_ack_loss_retry_sends_identical_event_and_deduplicates(self):
        self.initialize()
        calls = []

        def flaky_send(event):
            calls.append(copy.deepcopy(event))
            self.engine.receive(event)
            if len(calls) == 1:
                raise TimeoutError("simulacao de perda de ACK local")

        self.source.send_attribute = flaky_send
        change = self.rows[1]
        with self.assertRaises(TimeoutError):
            self.source.change(change)
        self.assertEqual(self.source.state()["pending_request_id"], change["request_id"])
        self.assertEqual(self.source.state()["attributes"]["atA"], 0)
        self.assertEqual(self.engine.state()["sequences"]["atA"], 1)

        result = self.source.change(change)
        self.assertTrue(result["changed"])
        self.assertEqual(calls[0], calls[1])  # Inclui mesmo emitted_at.
        self.assertEqual(self.source.state()["pending_request_id"], None)
        self.assertEqual(self.source.state()["attributes"]["atA"], 5)
        self.assertEqual(len(self.engine.state()["received_ids"]), 1)

    def test_nonzero_watermark_requires_replay_not_implemented(self):
        self.initialize()
        other = LogicEngine(lambda snapshot: None, lambda event: None)
        with self.assertRaisesRegex(ContractError, "replay nao implementado"):
            other.initialize({
                "schema_version": 1, "run_id": "other-run",
                "snapshot_version": "other-run:snapshot:1",
                "attributes": {"atA": 5, "atB": 0},
                "sequences": {"atA": 1, "atB": 0},
            })


if __name__ == "__main__":
    unittest.main()
