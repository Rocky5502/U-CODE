"""Synthetic-only one-A100 rental scenario sanity checks."""
from decimal import Decimal
import unittest

from scripts.estimate_ai_galaxy_rental import RentalScenario, scenario_from_cli


class RentalScenarioTests(unittest.TestCase):
    def test_forty_task_pilot_scenario(self):
        v = RentalScenario(40, 2, 1, Decimal(5), Decimal(8),
                           Decimal("0.25"))
        self.assertEqual(v.assignments, 480)
        self.assertEqual(v.gpu_hours, Decimal(50))
        self.assertEqual(v.gpu_days, Decimal(50)/24)
        self.assertEqual(v.nominal_rmb, Decimal(400))

    def test_full_study_exposes_compute_scale(self):
        s = RentalScenario(250, 8, 3, Decimal(5), Decimal(8),
                           Decimal(0))
        self.assertEqual(s.assignments, 36000)
        self.assertEqual(s.gpu_hours, Decimal(3000))
        self.assertEqual(s.gpu_days, Decimal(125))

    def test_six_models_mandatory(self):
        with self.assertRaisesRegex(ValueError, "all six"):
            RentalScenario(40, 2, 1, Decimal(5), Decimal(8),
                           model_count=5)

    def test_single_gpu_mandatory(self):
        with self.assertRaisesRegex(ValueError, "one A100"):
            RentalScenario(40, 2, 1, Decimal(5), Decimal(8),
                           gpu_count=2)

    def test_more_than_eight_policies_refused(self):
        with self.assertRaisesRegex(ValueError, "eight"):
            RentalScenario(40, 9, 1, Decimal(5), Decimal(8))

    def test_finite_nonnegative_time_and_price(self):
        for val in ("NaN", "Infinity", "-1"):
            with self.subTest(value=val):
                with self.assertRaises(ValueError):
                    RentalScenario(40, 2, 1, Decimal(val), Decimal(8))
        with self.assertRaises(ValueError):
            RentalScenario(40, 2, 1, Decimal(0), Decimal(8))
        with self.assertRaises(ValueError):
            RentalScenario(40, 2, 1, Decimal(5), Decimal("-8"))

    def test_no_claimed_experiments_or_qualified_tasks(self):
        v = RentalScenario(40, 2, 1, Decimal(5), Decimal(8)).to_dict()
        self.assertFalse(v["experiment_results_generated"])
        self.assertFalse(v["runnable_now"])
        self.assertEqual(v["approved_executable_task_count"],
                         "NOT_VERIFIED_BY_THIS_TOOL")

    def test_cli_requires_minutes_input(self):
        with self.assertRaises(SystemExit):
            scenario_from_cli([])

    def test_cli_respects_selected_roster(self):
        s = scenario_from_cli([
            "--tasks", "60", "--policies", "2", "--seeds", "1",
            "--minutes-per-assignment", "3", "--overhead-fraction", "0"])
        self.assertEqual(s.assignments, 720)
        self.assertEqual(s.gpu_hours, Decimal(36))
        self.assertEqual(s.gpu_count, 1)


if __name__ == "__main__":
    unittest.main()
