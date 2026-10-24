"""No real benchmark claims: independently checks printed toy counterexample."""
import unittest

from examples.conditional_dependence_smoke import run_demo


class ConditionalDependenceDemoTests(unittest.TestCase):
    def test_fitted_independence_vs_correlation_can_change_selection(self):
        x = run_demo()
        self.assertEqual(x["independent_first_action"], "a")
        self.assertAlmostEqual(x["independent_hypothetical_utility"], .285)
        self.assertEqual(x["redundant_first_action"], "abstain")
        self.assertEqual(x["redundant_hypothetical_utility"], 0)

    def test_demo_explicitly_warns_not_empirical(self):
        x = run_demo()
        self.assertIn("SYNTHETIC ONLY", x["evidence"])
        self.assertIn("zero third-party", x["evidence"])


if __name__ == "__main__":
    unittest.main()
