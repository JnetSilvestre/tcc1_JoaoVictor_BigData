"""Testes unitarios do validador de replay V05 (sem Docker)."""
import copy
import unittest

from c2.v05_duplicate import (
    EVENT_ID, EXPECTED, assert_prepared, validate_original, verify_after,
)


def original_event():
    return {**EXPECTED, "emitted_at": "2026-11-15T17:57:08.636308+00:00"}


def expected_states():
    shared = {
        "ready": True, "run_id": "v05-dedup-v1",
        "snapshot_version": "v05-dedup-v1:snapshot:0",
    }
    return {
        "attribute-source": {
            **shared, "service": "attribute-source",
            "attributes": {"atA": 5, "atB": 0},
            "sequences": {"atA": 1, "atB": 0}, "pending_request_id": None,
        },
        "logic-engine": {
            **shared, "service": "logic-engine",
            "attributes": {"atA": 5, "atB": 0},
            "sequences": {"atA": 1, "atB": 0},
            "received_ids": [EVENT_ID], "condition": False,
            "condition_sequence": 0, "condition_events": [], "faulted": False,
        },
        "rule-executor": {
            **shared, "service": "rule-executor", "approved": False,
            "condition_sequence": 0, "received_ids": [],
            "effects": [], "faulted": False,
        },
    }


class V05DuplicateTests(unittest.TestCase):
    def test_original_event_contract_valid(self):
        self.assertEqual(validate_original(original_event()), original_event())

    def test_rejects_different_timestamp_type(self):
        modified = original_event()
        modified["emitted_at"] = "not-a-date"
        with self.assertRaises(ValueError):
            validate_original(modified)

    def test_rejects_altered_payload(self):
        modified = original_event()
        modified["value"] = 7
        with self.assertRaisesRegex(ValueError, "nao corresponde"):
            validate_original(modified)

    def test_prepared_state_accepted(self):
        assert_prepared(expected_states())

    def test_prepared_state_rejects_existing_effect(self):
        altered = expected_states()
        altered["rule-executor"]["effects"].append({"event_id": "unexpected"})
        with self.assertRaisesRegex(ValueError, "executor"):
            assert_prepared(altered)

    def test_duplicate_log_and_unchanged_state_accepted(self):
        event = original_event()
        old = {"attribute-source": [], "logic-engine": [], "rule-executor": []}
        new = copy.deepcopy(old)
        new["logic-engine"].append({
            "event_type": "mutation", "path": "/notifications/attribute",
            "payload": event, "status": 200,
            "response": {"accepted": True, "duplicate": True},
        })
        s = expected_states()
        verify_after(s, copy.deepcopy(s), old, new, event)

    def test_replay_rejected_if_state_mutates(self):
        event = original_event()
        old = {"attribute-source": [], "logic-engine": [], "rule-executor": []}
        new = copy.deepcopy(old)
        new["logic-engine"].append({
            "event_type": "mutation", "path": "/notifications/attribute",
            "payload": event, "status": 200,
            "response": {"accepted": True, "duplicate": True},
        })
        s = expected_states()
        altered = copy.deepcopy(s)
        altered["logic-engine"]["sequences"]["atA"] = 2
        with self.assertRaisesRegex(ValueError, "estados mudaram"):
            verify_after(s, altered, old, new, event)


if __name__ == "__main__":
    unittest.main()
