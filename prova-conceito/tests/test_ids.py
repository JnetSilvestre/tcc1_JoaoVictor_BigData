"""Regressões de registro de IDs do Notifier e NOPManager."""

import unittest

from pon import Attribute, NOPManager


class IdRegistryTests(unittest.TestCase):

    def test_duplicate_id_does_not_replace_registered_entity(self):
        manager = NOPManager.GetInstance()
        original = Attribute(1, id=970001)
        self.addCleanup(original.setId, 0)
        self.assertIs(manager.entities[970001], original)

        with self.assertRaisesRegex(ValueError, "already registered"):
            Attribute(2, id=970001)
        self.assertIs(manager.entities[970001], original)

        newcomer = Attribute(2)
        self.addCleanup(newcomer.setId, 0)
        with self.assertRaisesRegex(ValueError, "already registered"):
            newcomer.setId(970001)

        self.assertEqual(newcomer.getId(), 0)
        self.assertIs(manager.entities[970001], original)

    def test_id_reassignment_and_unregister_are_consistent(self):
        manager = NOPManager.GetInstance()
        attribute = Attribute(1, id=970002)
        self.addCleanup(attribute.setId, 0)
        self.assertIs(manager.entities[970002], attribute)

        attribute.setId(970003)
        self.assertNotIn(970002, manager.entities)
        self.assertIs(manager.entities[970003], attribute)

        attribute.setId(970003)  # No-op, mesma entidade.
        attribute.setId(0)
        self.assertNotIn(970003, manager.entities)
        self.assertEqual(attribute.getId(), 0)

    def test_invalid_ids_are_rejected_without_changing_state(self):
        attribute = Attribute(0)
        for invalid in (-1, True, False, "7", 1.5):
            with self.subTest(id=invalid):
                with self.assertRaises(ValueError):
                    attribute.setId(invalid)
                self.assertEqual(attribute.getId(), 0)

    def test_remove_entity_must_not_remove_a_different_owner(self):
        manager = NOPManager.GetInstance()
        owner = Attribute(7, id=970004)
        self.addCleanup(owner.setId, 0)

        class StaleReference:
            def getId(self):
                return 970004

        manager.removeEntity(StaleReference())
        self.assertIs(manager.entities[970004], owner)


if __name__ == "__main__":
    unittest.main()
