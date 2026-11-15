"""Oito testes unitarios locais E08-D17K; sem Docker nem HTTP."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from c2.v05_condition_first import (
    ATTRIBUTE_ID, CONDITION_ID, EFFECT_ID, EVENT_ID, RUN_ID, SNAPSHOT,
    CHANGE, assert_change_response, check_hashes, expected_effect,
    validate_after, verify_logs,
)


def attribute():
    return {"schema_version": 1, "event_id": ATTRIBUTE_ID,
            "run_id": RUN_ID, "source": "attribute-source",
            "entity_id": "atB", "sequence": 1, "value": 1,
            "step": 2, "request_id": CHANGE["request_id"],
            "emitted_at": "2026-11-15T19:00:00+00:00"}


def condition():
    return {"schema_version": 1, "event_id": CONDITION_ID,
            "run_id": RUN_ID, "source": "logic-engine",
            "entity_id": "cn1", "sequence": 1, "approved": True,
            "caused_by": ATTRIBUTE_ID, "step": 2,
            "emitted_at": "2026-11-15T19:00:01+00:00"}


def states():
    common = {"ready": True, "run_id": RUN_ID,
              "snapshot_version": SNAPSHOT}
    return {
        "attribute-source": {
            **common, "service": "attribute-source",
            "attributes": {"atA": 5, "atB": 1},
            "sequences": {"atA": 1, "atB": 1}, "pending_request_id": None,
        },
        "logic-engine": {
            **common, "service": "logic-engine",
            "attributes": {"atA": 5, "atB": 1},
            "sequences": {"atA": 1, "atB": 1},
            "received_ids": [EVENT_ID, ATTRIBUTE_ID], "condition": True,
            "condition_sequence": 1, "condition_events": [condition()],
            "faulted": False,
        },
        "rule-executor": {
            **common, "service": "rule-executor", "approved": True,
            "condition_sequence": 1, "received_ids": [CONDITION_ID],
            "effects": [expected_effect()], "faulted": False,
        },
    }


def logs():
    accepted = {"accepted": True, "duplicate": False}
    attr, cond, eff = attribute(), condition(), expected_effect()
    return {
        "attribute-source": [
            {"event_type": "send", "path": "/notifications/attribute",
             "payload": attr},
            {"event_type": "ack", "path": "/notifications/attribute",
             "payload": attr, "response": accepted},
            {"event_type": "mutation", "path": "/attributes/change",
             "payload": CHANGE, "status": 200},
        ],
        "logic-engine": [
            {"event_type": "send", "path": "/notifications/condition",
             "payload": cond},
            {"event_type": "ack", "path": "/notifications/condition",
             "payload": cond, "response": accepted},
            {"event_type": "mutation", "path": "/notifications/attribute",
             "payload": attr, "status": 200, "response": accepted},
        ],
        "rule-executor": [
            {"event_type": "effect", "payload": eff},
            {"event_type": "mutation", "path": "/notifications/condition",
             "payload": cond, "status": 200, "response": accepted},
        ],
    }


class V05ConditionFirstTests(unittest.TestCase):
    def test_state_after_one_condition_and_effect(self):
        self.assertEqual(validate_after(states()), (condition(), expected_effect()))

    def test_missing_effect_rejected(self):
        state = states()
        state["rule-executor"]["effects"] = []
        with self.assertRaisesRegex(ValueError, "executor"):
            validate_after(state)

    def test_wrong_condition_cause_rejected(self):
        state = states()
        state["logic-engine"]["condition_events"][0]["caused_by"] = "wrong"
        with self.assertRaisesRegex(ValueError, "ConditionChanged"):
            validate_after(state)

    def test_valid_http_response(self):
        assert_change_response({"status": 200, "body": {
            "changed": True, "sequence": 1, "event_id": ATTRIBUTE_ID,
            "duplicate_request": False}})

    def test_duplicate_request_rejected(self):
        with self.assertRaisesRegex(ValueError, "resposta HTTP"):
            assert_change_response({"status": 200, "body": {
                "changed": True, "sequence": 1,
                "event_id": ATTRIBUTE_ID, "duplicate_request": True}})

    def test_logs_show_exact_single_causal_chain(self):
        old = {role: [] for role in logs()}
        self.assertEqual(verify_logs(old, logs(), condition(), expected_effect()), attribute())

    def test_duplicate_effect_log_rejected(self):
        old = {role: [] for role in logs()}
        new = logs()
        new["rule-executor"].append({"event_type": "effect", "payload": expected_effect()})
        with self.assertRaisesRegex(ValueError, "logs"):
            verify_logs(old, new, condition(), expected_effect())

    def test_sha_manifest_detects_modified_file(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            f = p / "evidence.json"
            f.write_bytes(b"original")
            sha = hashlib.sha256(f.read_bytes()).hexdigest()
            (p / "checksums.sha256").write_text(
                f"{sha}  evidence.json\n", encoding="utf-8")
            check_hashes(p, {"evidence.json"})
            f.write_bytes(b"alterado")
            with self.assertRaisesRegex(ValueError, "checksum"):
                check_hashes(p, {"evidence.json"})


if __name__ == "__main__":
    unittest.main()
