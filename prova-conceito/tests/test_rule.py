"""Validações de Rule, Action e Instigation da prova local (C0 parcial)."""

import asyncio
import unittest

from pon import Action, Attribute, Instigation, Rule


class RuleRegressionTests(unittest.TestCase):

    def _chain(self, effects, get_step=lambda: None):
        at_a = Attribute(0)
        at_b = Attribute(0)
        condition = (at_a >= 5) & (at_b == 1)

        def on_action():
            effects.append(get_step())

        action = Action([Instigation([on_action])])
        rule = Rule(condition, action)
        return at_a, at_b, condition, rule

    def test_seven_steps_trigger_exactly_two_effects_in_order(self):
        effects = []
        current_step = [0]
        at_a, at_b, condition, rule = self._chain(
            effects, get_step=lambda: current_step[0]
        )

        # Fixture mínima prevista na Etapa 05; expectativa: passos 3 e 7.
        steps = [
            (at_a, 0),
            (at_a, 5),
            (at_b, 1),
            (at_b, 1),
            (at_a, 6),
            (at_b, 0),
            (at_b, 1),
        ]
        for step, (attribute, value) in enumerate(steps, start=1):
            current_step[0] = step
            attribute.value = value

        self.assertEqual(effects, [3, 7])
        self.assertTrue(condition.approved())
        self.assertIsNotNone(rule)

    def test_action_executes_without_running_asyncio_loop(self):
        effects = []
        at_a, at_b, _, rule = self._chain(effects)
        at_a.value = 5
        at_b.value = 1

        self.assertEqual(effects, [None])
        self.assertIsNotNone(rule)

    def test_action_executes_synchronously_inside_asyncio_loop(self):
        effects = []
        at_a, at_b, _, rule = self._chain(effects)

        async def scenario():
            at_a.value = 5
            at_b.value = 1
            # Efeito já deve existir sem necessidade de sleep/drain.
            self.assertEqual(effects, [None])

        asyncio.run(scenario())
        self.assertIsNotNone(rule)

    def test_explicit_awaitable_execute_keeps_compatibility(self):
        effects = []
        _, _, _, rule = self._chain(effects)

        asyncio.run(rule.execute())
        self.assertEqual(effects, [None])


if __name__ == "__main__":
    unittest.main()
