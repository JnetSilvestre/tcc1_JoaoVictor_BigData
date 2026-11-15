"""Regressao local E08-D17H; nenhuma chamada HTTP ou Docker."""
import copy
import unittest

from c2.v05_conflict import (
    EXPECTED_ERROR, check_conflict_reply, conflict_event,
    previous_events, verify_after,
)
from c2.v05_duplicate import EXPECTED, EVENT_ID


def event():
    return {**EXPECTED, "emitted_at": "2026-11-15T17:57:08.636308+00:00"}


def logs(original):
    a = {
        "attribute-source": [{"event_type": "listening"}],
        "logic-engine": [
            {
                "event_type": "mutation", "path": "/notifications/attribute",
                "payload": original, "status": 200,
                "response": {"accepted": True, "duplicate": False},
            },
            {
                "event_type": "mutation", "path": "/notifications/attribute",
                "payload": original, "status": 200,
                "response": {"accepted": True, "duplicate": True},
            },
        ],
        "rule-executor": [{"event_type": "listening"}],
    }
    return a


class V05ConflictTests(unittest.TestCase):
    def test_conflict_changes_only_value(self):
        first = event()
        second = conflict_event(first)
        self.assertEqual(first["value"], 5)
        self.assertEqual(second["value"], 6)
        self.assertEqual(first["event_id"], second["event_id"])
        self.assertEqual(first["emitted_at"], second["emitted_at"])

    def test_previous_log_pattern_accepted(self):
        previous_events(logs(event()), event())

    def test_previous_log_rejects_second_conflict(self):
        prior = logs(event())
        prior["logic-engine"].append({
            "event_type": "mutation", "path": "/notifications/attribute",
            "payload": event(), "status": 409,
        })
        with self.assertRaises(ValueError):
            previous_events(prior, event())

    def test_response_409_accepted(self):
        check_conflict_reply({"status": 409, "body": {"error": EXPECTED_ERROR}})

    def test_response_wrong_code_rejected(self):
        with self.assertRaises(ValueError):
            check_conflict_reply({"status": 200, "body": {"error": EXPECTED_ERROR}})

    def test_rejection_preserves_state_and_adds_one_log(self):
        orig = event()
        changed = conflict_event(orig)
        before = logs(orig)
        after = copy.deepcopy(before)
        after["logic-engine"].append({
            "event_type": "mutation", "path": "/notifications/attribute",
            "payload": changed, "status": 409,
            "response": {"error": EXPECTED_ERROR},
        })
        states = {"logic-engine": {"received_ids": [EVENT_ID]}}
        verify_after(states, copy.deepcopy(states), before, after, changed)

    def test_rejection_detects_state_change(self):
        orig = event()
        changed = conflict_event(orig)
        before = logs(orig)
        after = copy.deepcopy(before)
        after["logic-engine"].append({
            "event_type": "mutation", "path": "/notifications/attribute",
            "payload": changed, "status": 409,
            "response": {"error": EXPECTED_ERROR},
        })
        with self.assertRaises(ValueError):
            verify_after({"a": 1}, {"a": 2}, before, after, changed)


if __name__ == "__main__":
    unittest.main()
