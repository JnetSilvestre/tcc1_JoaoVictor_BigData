"""Testes dos contratos C1. Não inicia processos nem servidor HTTP."""
import unittest
from c1.protocol import (
    ContractError, utc_now, validate_change, validate_snapshot,
    validate_executor_snapshot, validate_attribute_event, validate_condition_event,
)


class ContractsTests(unittest.TestCase):
    def setUp(self):
        self.time = utc_now()
        self.change = {"run_id": "r1", "request_id": "req-1", "entity_id": "atA", "value": 5, "step": 2}
        self.snapshot = {
            "schema_version": 1, "run_id": "r1", "snapshot_version": "r1:snapshot:0",
            "attributes": {"atA": 0, "atB": 0}, "sequences": {"atA": 0, "atB": 0},
        }
        self.attribute = {
            "schema_version": 1, "event_id": "r1:atA:1", "run_id": "r1",
            "source": "attribute-source", "entity_id": "atA", "sequence": 1,
            "value": 5, "emitted_at": self.time, "step": 2, "request_id": "req-1",
        }
        self.condition = {
            "schema_version": 1, "event_id": "r1:cn1:1", "run_id": "r1",
            "source": "logic-engine", "entity_id": "cn1", "sequence": 1,
            "approved": True, "caused_by": "r1:atB:1",
            "emitted_at": self.time, "step": 3,
        }

    def test_valid_payloads(self):
        self.assertEqual(validate_change(self.change), self.change)
        self.assertEqual(validate_snapshot(self.snapshot), self.snapshot)
        self.assertEqual(validate_attribute_event(self.attribute), self.attribute)
        self.assertEqual(validate_condition_event(self.condition), self.condition)
        self.assertTrue(validate_executor_snapshot({
            "schema_version": 1, "run_id": "r1",
            "snapshot_version": "r1:snapshot:0",
            "condition_sequence": 0, "approved": False,
        }))

    def test_change_wrong_type_or_unknown_id(self):
        for field, value in (("value", True), ("entity_id", "unknown"), ("step", 0), ("request_id", "")):
            with self.subTest(field=field):
                with self.assertRaises(ContractError):
                    validate_change({**self.change, field: value})

    def test_change_missing_or_extra_field(self):
        for obj in (
            {k: v for k, v in self.change.items() if k != "run_id"},
            {**self.change, "other": 1},
        ):
            with self.assertRaises(ContractError):
                validate_change(obj)

    def test_snapshot_types_and_watermarks(self):
        with self.assertRaises(ContractError):
            validate_snapshot({**self.snapshot, "sequences": {"atA": -1, "atB": 0}})
        with self.assertRaises(ContractError):
            validate_snapshot({**self.snapshot, "attributes": {"atA": False, "atB": 0}})

    def test_attribute_rejects_wrong_version_or_id(self):
        for key, value in (("schema_version", 2), ("event_id", "r1:atA:2"), ("sequence", 0), ("value", True)):
            with self.subTest(key=key):
                with self.assertRaises(ContractError):
                    validate_attribute_event({**self.attribute, key: value})

    def test_condition_rejects_bad_approval_or_cause(self):
        for key, value in (("approved", 1), ("caused_by", ""), ("event_id", "r1:cn2:1"), ("source", "invalid")):
            with self.subTest(key=key):
                with self.assertRaises(ContractError):
                    validate_condition_event({**self.condition, key: value})

    def test_timestamp_requires_utc(self):
        for stamp in ("2026-11-12T20:12:00", "not-a-time", "2026-11-12T17:12:00-03:00"):
            with self.subTest(stamp=stamp):
                with self.assertRaises(ContractError):
                    validate_attribute_event({**self.attribute, "emitted_at": stamp})


if __name__ == "__main__":
    unittest.main()
