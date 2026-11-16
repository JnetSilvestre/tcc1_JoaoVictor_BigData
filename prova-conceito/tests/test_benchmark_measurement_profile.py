"""E11-M00B: testes sinteticos, sem Docker, kubectl, snapshot ou POST."""
import unittest

from benchmark.measurement_profile import (
    MODES, RESOURCES_DIAGNOSTIC, TIMING_ONLY,
    not_collected_quality, profile_record, select_sampler,
)


class MeasurementProfileTests(unittest.TestCase):
    def test_timing_only_does_not_construct_sampler(self):
        def forbidden():
            raise AssertionError("sonda nao deveria ser construida")
        self.assertIsNone(select_sampler(TIMING_ONLY, forbidden))
        record = profile_record(TIMING_ONLY)
        self.assertFalse(record["resource_sampling_during_batch"])

    def test_diagnostic_mode_keeps_previous_sampler_behavior(self):
        sentinel = object()
        self.assertIs(select_sampler(RESOURCES_DIAGNOSTIC, lambda: sentinel), sentinel)
        self.assertTrue(profile_record(RESOURCES_DIAGNOSTIC)["resource_sampling_during_batch"])

    def test_unknown_mode_is_fail_closed(self):
        self.assertEqual(len(MODES), 2)
        with self.assertRaises(ValueError):
            select_sampler("invalid", lambda: None)
        with self.assertRaises(ValueError):
            profile_record("invalid")

    def test_absent_metrics_are_never_zero_or_approved(self):
        quality = not_collected_quality()
        self.assertEqual(quality["status"], "NOT_COLLECTED")
        self.assertIsNone(quality["sample_count"])
        self.assertIsNone(quality["cpu_window_adequate"])
        self.assertIsNone(quality["memory_window_adequate"])
        self.assertFalse(quality["usable_cpu"])
        self.assertFalse(quality["usable_memory"])
        self.assertFalse(quality["measurement_approved"])


if __name__ == "__main__":
    unittest.main()
