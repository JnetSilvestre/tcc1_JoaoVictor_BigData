"""Testes puros de pré-condição E08-D11; não acessam o Docker."""
import copy
import unittest

from c2.runner import check_snapshot_state


class C2RunnerPreflightTests(unittest.TestCase):
    def setUp(self):
        run_id = "c0-minimo-v1"
        base = {"ready": True, "run_id": run_id,
                "snapshot_version": f"{run_id}:snapshot:0"}
        attr = {"attributes": {"atA": 0, "atB": 0},
                "sequences": {"atA": 0, "atB": 0}}
        self.states = {
            "attribute-source": {**base, **copy.deepcopy(attr), "pending_request_id": None},
            "logic-engine": {**base, **copy.deepcopy(attr), "condition": False,
                             "condition_sequence": 0, "received_ids": [],
                             "condition_events": [], "faulted": False},
            "rule-executor": {**base, "approved": False, "condition_sequence": 0,
                              "effects": [], "received_ids": [], "faulted": False},
        }

    def test_clean_snapshot_is_accepted(self):
        check_snapshot_state(self.states, "c0-minimo-v1")

    def test_rejects_attribute_already_processed(self):
        self.states["attribute-source"]["sequences"]["atA"] = 1
        with self.assertRaises(ValueError):
            check_snapshot_state(self.states, "c0-minimo-v1")

    def test_rejects_effect_already_produced(self):
        self.states["rule-executor"]["effects"] = [{"step": 3}]
        with self.assertRaises(ValueError):
            check_snapshot_state(self.states, "c0-minimo-v1")


if __name__ == "__main__":
    unittest.main()
