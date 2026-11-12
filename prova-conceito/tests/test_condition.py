"""Regressões de Condition na prova Python do TCC2 (sem dependências externas)."""

import unittest

from pon import Attribute, Condition


class Recorder:
    def __init__(self, condition):
        self.condition = condition
        self.notifications = []

    def update(self, notifier_id):
        self.notifications.append(
            {"notifier_id": notifier_id, "approved": self.condition.approved()}
        )


class ConditionRegressionTests(unittest.TestCase):
    def build_chain(self):
        at_a = Attribute(0)
        at_b = Attribute(0)
        condition = (at_a >= 5) & (at_b == 1)
        return at_a, at_b, condition

    def test_condition_approves_only_when_both_premises_are_true(self):
        at_a, at_b, condition = self.build_chain()
        self.assertFalse(condition.approved())

        at_a.value = 5
        self.assertFalse(condition.approved())

        at_b.value = 1
        self.assertTrue(condition.approved())

    def test_notifications_only_on_condition_transitions(self):
        at_a, at_b, condition = self.build_chain()
        recorder = Recorder(condition)
        condition.register(recorder)

        # Fixture minima da Etapa 05, com dois efeitos esperados em passos 3/7.
        at_a.value = 0
        at_a.value = 5
        at_b.value = 1
        at_b.value = 1
        at_a.value = 6
        at_b.value = 0
        at_b.value = 1

        self.assertEqual(
            recorder.notifications,
            [
                {"notifier_id": 0, "approved": True},
                {"notifier_id": 0, "approved": False},
                {"notifier_id": 0, "approved": True},
            ],
        )
        self.assertEqual(
            sum(n["approved"] for n in recorder.notifications), 2
        )

    def test_nested_conditions_propagate_to_observers(self):
        at_a = Attribute(0)
        at_b = Attribute(0)
        at_c = Attribute(0)
        inner = (at_a >= 5) & (at_b == 1)
        outer = inner & (at_c == 7)
        recorder = Recorder(outer)
        outer.register(recorder)

        at_a.value = 5
        at_b.value = 1
        self.assertTrue(inner.approved())
        self.assertFalse(outer.approved())
        self.assertEqual(recorder.notifications, [])

        at_c.value = 7
        self.assertEqual(recorder.notifications, [
            {"notifier_id": 0, "approved": True}
        ])


if __name__ == "__main__":
    unittest.main()
