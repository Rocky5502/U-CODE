"""Synthetic demo contract is deliberately not a scientific performance test."""
import unittest

from examples.bes_lookahead_smoke import run_demo


class BesDemoTests(unittest.TestCase):
    def test_two_stage_option_value_is_visible_only_in_lookahead(self):
        r = run_demo()
        self.assertEqual(r["one_step_action"], "abstain")
        self.assertEqual(r["two_step_action"], "synthetic-test-a")
        self.assertAlmostEqual(r["hypothetical_two_step_net_utility"], .285)

    def test_demo_labels_all_evidence_fabricated_and_charges_budget(self):
        r = run_demo()
        self.assertIn("SYNTHETIC", r["warning"])
        self.assertIn("zero executed", r["warning"])
        self.assertAlmostEqual(r["fabricated_two_positive_posterior"], 16 / 17)
        self.assertEqual(r["remaining_test_calls_after_two_fabricated_positives"], 0)


if __name__ == "__main__":
    unittest.main()
