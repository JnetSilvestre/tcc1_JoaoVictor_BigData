"""E08-D17P: testes puros, sem daemon Docker e sem POST."""
import copy
import unittest

from c2.v05_condition_conflict import (
    EXPECTED_ERROR, assert_conflict_reply, conflict_event, verify_conflict,
)
from c2.v05_condition_first import CONDITION_ID, ATTRIBUTE_ID


def event():
    return {
        "schema_version": 1, "event_id": CONDITION_ID,
        "run_id": "v05-dedup-v1", "source": "logic-engine",
        "entity_id": "cn1", "sequence": 1, "approved": True,
        "caused_by": ATTRIBUTE_ID, "step": 2,
        "emitted_at": "2026-11-15T19:03:59.142115+00:00",
    }


def states():
    return {
        "attribute-source": {"attributes": {"atA": 5, "atB": 1}},
        "logic-engine": {"condition": True},
        "rule-executor": {"effects": [{"event_id": "v05-dedup-v1:rl1:1"}]},
    }


def logs():
    return {
        "attribute-source": [{"event_type": "listening"}],
        "logic-engine": [{"event_type": "listening"}],
        "rule-executor": [{"event_type": "listening"}],
    }


def rejection(payload):
    return {
        "event_type": "mutation", "path": "/notifications/condition",
        "payload": payload, "status": 409,
        "response": {"error": EXPECTED_ERROR},
    }


class V05ConditionConflictTests(unittest.TestCase):
    def test_changes_only_approved(self):
        original = event()
        changed = conflict_event(original)
        self.assertIs(original["approved"], True)
        self.assertIs(changed["approved"], False)
        self.assertEqual(
            [k for k in original if original[k] != changed[k]],
            ["approved"])
        self.assertEqual(changed["emitted_at"], original["emitted_at"])

    def test_rejects_incorrect_original(self):
        bad = event()
        bad["approved"] = False
        with self.assertRaisesRegex(ValueError, "inesperada"):
            conflict_event(bad)

    def test_http_409_expected_body(self):
        assert_conflict_reply({
            "status": 409, "body": {"error": EXPECTED_ERROR}})

    def test_wrong_http_fails(self):
        with self.assertRaisesRegex(ValueError, "HTTP"):
            assert_conflict_reply({
                "status": 200, "body": {"accepted": True, "duplicate": True}})

    def test_wrong_error_fails(self):
        with self.assertRaisesRegex(ValueError, "HTTP"):
            assert_conflict_reply({
                "status": 409, "body": {"error": "outro"}})

    def test_unchanged_states_and_single_log_pass(self):
        before = states()
        logs_before = logs()
        logs_after = copy.deepcopy(logs_before)
        logs_after["rule-executor"].append(rejection(conflict_event(event())))
        verify_conflict(
            before, copy.deepcopy(before),
            logs_before, logs_after, conflict_event(event()))

    def test_state_mutation_rejected(self):
        before = states()
        after = copy.deepcopy(before)
        after["rule-executor"]["effects"].append({"event_id": "extra"})
        logs_before = logs()
        logs_after = copy.deepcopy(logs_before)
        logs_after["rule-executor"].append(rejection(conflict_event(event())))
        with self.assertRaisesRegex(ValueError, "estado"):
            verify_conflict(
                before, after, logs_before, logs_after, conflict_event(event()))

    def test_nonmatching_payload_log_rejected(self):
        before = states()
        logs_before = logs()
        logs_after = copy.deepcopy(logs_before)
        logs_after["rule-executor"].append(rejection(event()))
        with self.assertRaisesRegex(ValueError, "log"):
            verify_conflict(
                before, before, logs_before, logs_after, conflict_event(event()))


if __name__ == "__main__":
    unittest.main()
