"""Analytical properties of a *hypothetical* binary diagnostic model."""
import math
import unittest

from ucode.voi import (
    DiagnosticAction, ReleaseRule, terminal_value, value_of_diagnostic,
    choose_diagnostic,
)


class EvidenceValueTests(unittest.TestCase):
    def setUp(self):
        self.rule = ReleaseRule(
            max_predicted_failure=0.1, correct_reward=1.0,
            failure_penalty=1.0, unit_cost_penalty=0.1,
        )

    def test_perfect_diagnostic_value_hand_calculation(self):
        test = DiagnosticAction("test", 1.0, 1.0, cost=1)
        result = value_of_diagnostic(0.5, test, self.rule)
        self.assertEqual(result.terminal_value_before, 0)
        self.assertAlmostEqual(result.positive_probability, 0.5)
        self.assertAlmostEqual(result.negative_probability, 0.5)
        self.assertAlmostEqual(result.posterior_positive, 1.0)
        self.assertAlmostEqual(result.posterior_negative, 0.0)
        self.assertAlmostEqual(result.expected_terminal_value_after, 0.5)
        self.assertAlmostEqual(result.gross_value_of_information, 0.5)
        self.assertAlmostEqual(result.net_gain, 0.4)

    def test_noninformative_diagnostic_has_no_value(self):
        test = DiagnosticAction("lint", sensitivity=0.7,
                                specificity=0.3, cost=1)
        result = value_of_diagnostic(0.5, test, self.rule)
        self.assertAlmostEqual(result.posterior_positive, 0.5)
        self.assertAlmostEqual(result.posterior_negative, 0.5)
        self.assertAlmostEqual(result.gross_value_of_information, 0.0)
        self.assertIsNone(choose_diagnostic(0.5, [test], self.rule, 10))

    def test_posterior_martingale(self):
        diag = DiagnosticAction("static_analysis", .8, .9, 0.5)
        for prior in (0., .01, .1, .5, .8, .99, 1.):
            result = value_of_diagnostic(prior, diag, self.rule)
            recovered = (result.positive_probability * result.posterior_positive
                         + result.negative_probability * result.posterior_negative)
            self.assertAlmostEqual(recovered, prior)

    def test_no_improvement_for_known_outcome(self):
        diag = DiagnosticAction("test", 1, 1, .5)
        for p in (0., 1.):
            self.assertAlmostEqual(
                value_of_diagnostic(p, diag, self.rule).gross_value_of_information, 0)

    def test_risk_gated_release_contraindication(self):
        # Release threshold can make the *signed* evidence value negative:
        # a noisy diagnostic can move an admissible candidate below threshold.
        diag = DiagnosticAction("noisy_test", .8, .8, 1)
        val = value_of_diagnostic(.91, diag, self.rule)
        self.assertLess(val.gross_value_of_information, 0)
        self.assertIsNone(choose_diagnostic(.91, [diag], self.rule, 3))

    def test_budget_and_cost_are_real_constraints(self):
        diag = DiagnosticAction("expensive_test", 1, 1, 2)
        self.assertIsNone(choose_diagnostic(.5, [diag], self.rule, 1))
        value = choose_diagnostic(.5, [diag], self.rule, 2)
        self.assertIsNotNone(value)
        self.assertAlmostEqual(value.net_gain, .3)
        self.assertEqual(value.action, "expensive_test")

    def test_selects_evidence_gain_not_cheapest(self):
        wrong = DiagnosticAction("uninformative_test", .5, .5, .2)
        best = DiagnosticAction("informative_test", 1, 1, 1)
        out = choose_diagnostic(.5, [wrong, best], self.rule, 2)
        self.assertEqual(out.action, "informative_test")

    def test_equal_action_values_use_stable_input_order(self):
        a = DiagnosticAction("first", 1, 1, 1)
        b = DiagnosticAction("second", 1, 1, 1)
        self.assertEqual(choose_diagnostic(.5, [a, b], self.rule, 1).action,
                         "first")

    def test_hard_release_threshold(self):
        self.assertEqual(terminal_value(.89, self.rule), 0)
        self.assertGreater(terminal_value(.95, self.rule), 0)

    def test_unreachable_binary_branch_finite(self):
        always_fails = DiagnosticAction("always_negative", 0, 1, 1)
        r = value_of_diagnostic(0.7, always_fails, self.rule)
        self.assertEqual(r.positive_probability, 0)
        self.assertTrue(math.isfinite(r.posterior_positive))
        self.assertAlmostEqual(r.posterior_negative, 0.7)

    def test_reject_invalid_inputs(self):
        with self.assertRaises(ValueError):
            DiagnosticAction("bad", .5, .5, 0)
        with self.assertRaises(ValueError):
            DiagnosticAction("bad", 2, .5, 1)
        with self.assertRaises(ValueError):
            DiagnosticAction("bad", .5, float("nan"), 1)
        with self.assertRaises(ValueError):
            ReleaseRule(1.01)
        with self.assertRaises(ValueError):
            ReleaseRule(0.1, unit_cost_penalty=-1)
        with self.assertRaises(ValueError):
            terminal_value(-.1, self.rule)
        with self.assertRaises(ValueError):
            choose_diagnostic(.5, [], self.rule, float("inf"))


if __name__ == "__main__":
    unittest.main()
