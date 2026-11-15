"""Regressao E08-D17M sem Docker/POST."""
import copy
import unittest

from c2.v05_condition_replay import (
    assert_replay_response, validate_replay,
)
from c2.v05_condition_first import CONDITION_ID


def condition():
    return {
        "schema_version": 1, "event_id": CONDITION_ID,
        "run_id": "v05-dedup-v1", "source": "logic-engine",
        "entity_id": "cn1", "sequence": 1, "approved": True,
        "caused_by": "v05-dedup-v1:atB:1", "step": 2,
        "emitted_at": "2026-11-15T19:03:59.142115+00:00",
    }


def logs():
    return {
        "attribute-source": [{"event_type": "listening"}],
        "logic-engine": [{"event_type": "listening"}],
        "rule-executor": [{"event_type": "effect"}],
    }


def state():
    return {
        "attribute-source": {"atA": 5, "atB": 1},
        "logic-engine": {"condition": True},
        "rule-executor": {"approved": True, "effects": [{"event_id": "rl1"}]},
    }


def replay_log(payload):
    return {
        "event_type": "mutation", "path": "/notifications/condition",
        "payload": payload, "status": 200,
        "response": {"accepted": True, "duplicate": True},
    }


class V05ConditionReplayTests(unittest.TestCase):
    def test_ack_duplicate_accepted(self):
        assert_replay_response({
            "status": 200, "body": {"accepted": True, "duplicate": True}})

    def test_nondeduplicated_rejected(self):
        with self.assertRaisesRegex(ValueError, "ACK"):
            assert_replay_response({
                "status": 200, "body": {"accepted": True, "duplicate": False}})

    def test_http_409_rejected(self):
        with self.assertRaisesRegex(ValueError, "ACK"):
            assert_replay_response({"status": 409, "body": {"error": "conflict"}})

    def test_correct_log_and_state_accepted(self):
        previous = logs()
        after = copy.deepcopy(previous)
        after["rule-executor"].append(replay_log(condition()))
        before_state = state()
        validate_replay(before_state, copy.deepcopy(before_state),
                        previous, after, condition())

    def test_double_response_log_rejected(self):
        previous = logs()
        after = copy.deepcopy(previous)
        after["rule-executor"].extend(
            [replay_log(condition()), replay_log(condition())])
        with self.assertRaisesRegex(ValueError, "exatamente"):
            validate_replay(state(), state(), previous, after, condition())

    def test_effect_duplication_rejected(self):
        previous = logs()
        after = copy.deepcopy(previous)
        after["rule-executor"].append(replay_log(condition()))
        changed = state()
        changed["rule-executor"]["effects"].append({"event_id": "rl2"})
        with self.assertRaisesRegex(ValueError, "estado"):
            validate_replay(state(), changed, previous, after, condition())

    def test_wrong_payload_rejected(self):
        previous = logs()
        after = copy.deepcopy(previous)
        unexpected = dict(condition())
        unexpected["approved"] = False
        after["rule-executor"].append(replay_log(unexpected))
        with self.assertRaisesRegex(ValueError, "log"):
            validate_replay(state(), state(), previous, after, condition())

    def test_source_logs_change_rejected(self):
        previous = logs()
        after = copy.deepcopy(previous)
        after["rule-executor"].append(replay_log(condition()))
        after["attribute-source"].append({"event_type": "extra"})
        with self.assertRaisesRegex(ValueError, "fora do executor"):
            validate_replay(state(), state(), previous, after, condition())


if __name__ == "__main__":
    unittest.main()
