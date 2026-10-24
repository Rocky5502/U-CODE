"""Offline invariants for vector-budget, pre-outcome one-step policy."""
import unittest

from ucode.voi import ReleaseRule
from ucode.vector_policy import (
    DiagnosticForecast, GenerativeForecast, ResourcePrices,
    ResourceVector, choose_next_intervention,
)


class VectorBudgetPolicyTests(unittest.TestCase):
    def setUp(self):
        self.rule = ReleaseRule(max_predicted_failure=.1)
        self.budget = ResourceVector(tokens=100, test_calls=2,
                                     gpu_seconds=30, cpu_seconds=20,
                                     wall_seconds=60)
        self.prices = ResourcePrices(tokens=.001, test_calls=.1,
                                     gpu_seconds=.01, wall_seconds=.001)

    def test_hard_budgets_each_dimension(self):
        for cost in (ResourceVector(tokens=101), ResourceVector(test_calls=3),
                     ResourceVector(gpu_seconds=31), ResourceVector(cpu_seconds=21),
                     ResourceVector(wall_seconds=61)):
            self.assertFalse(self.budget.affordable(cost))
            with self.assertRaises(ValueError):
                self.budget.subtract(cost)

    def test_budget_exact_boundary(self):
        rem = self.budget.subtract(self.budget)
        self.assertTrue(rem.is_free())
        self.assertTrue(self.budget.affordable(self.budget))

    def test_fractional_price_and_integer_usage(self):
        self.assertAlmostEqual(ResourceVector(tokens=100).total_price(self.prices), .1)
        with self.assertRaises(ValueError):
            ResourceVector(test_calls=.5)
        with self.assertRaises(ValueError):
            ResourceVector(tokens=1.5)
        with self.assertRaises(ValueError):
            ResourcePrices(tokens=-.1)

    def test_hypothetical_perfect_test_reduces_budget(self):
        test = DiagnosticForecast("test", 1, 1, ResourceVector(test_calls=1))
        choice = choose_next_intervention(.5, [test], self.budget,
                                          self.prices, self.rule)
        self.assertEqual(choice.action, "test")
        self.assertAlmostEqual(choice.predicted_net_improvement, .4)
        self.assertEqual(choice.budget_after.test_calls, 1)
        self.assertEqual(choice.budget_after.tokens, 100)

    def test_noninformative_test_not_purchased(self):
        test = DiagnosticForecast("test", .7, .3, ResourceVector(test_calls=1))
        choice = choose_next_intervention(.5, [test], self.budget,
                                          self.prices, self.rule)
        self.assertEqual(choice.action, "abstain")

    def test_no_candidate_only_generation_is_feasible(self):
        diagnostic = DiagnosticForecast("retrieve", 1, 1, ResourceVector(tokens=2))
        generate = GenerativeForecast("generate", .6, ResourceVector(tokens=4))
        choice = choose_next_intervention(None, [diagnostic, generate],
                                          self.budget, self.prices, self.rule)
        self.assertEqual(choice.action, "generate")
        self.assertEqual(choice.budget_after.tokens, 96)

    def test_no_candidate_cannot_repair(self):
        repair = GenerativeForecast("repair", .7, ResourceVector(tokens=4))
        choice = choose_next_intervention(None, [repair], self.budget,
                                          self.prices, self.rule)
        self.assertEqual(choice.action, "abstain")

    def test_diagnostic_and_generation_use_same_terminal_utility(self):
        diagnostic = DiagnosticForecast("test", 1, 1, ResourceVector(test_calls=1))
        generate = GenerativeForecast("generate", .35, ResourceVector(tokens=10))
        choice = choose_next_intervention(.5, [generate, diagnostic],
                                          self.budget, self.prices, self.rule)
        self.assertEqual(choice.action, "test")  # .5-.1 beats .35-.01

    def test_repair_vs_test_risk_reduction(self):
        repair = GenerativeForecast("repair", .95, ResourceVector(tokens=10))
        test = DiagnosticForecast("static_analysis", .7, .7,
                                  ResourceVector(cpu_seconds=4))
        choice = choose_next_intervention(.2, [test, repair],
                                          self.budget, self.prices, self.rule)
        self.assertEqual(choice.action, "repair")

    def test_positive_cost_but_no_feasible_action_release(self):
        costly = DiagnosticForecast("test", 1, 1, ResourceVector(test_calls=3))
        choice = choose_next_intervention(.95, [costly], self.budget,
                                          self.prices, self.rule)
        self.assertEqual(choice.action, "release")
        self.assertEqual(choice.budget_after, self.budget)

    def test_negative_signed_evidence_value_is_respected(self):
        noisy = DiagnosticForecast("test", .8, .8, ResourceVector(test_calls=1))
        choice = choose_next_intervention(.91, [noisy], self.budget,
                                          self.prices, self.rule)
        self.assertEqual(choice.action, "release")

    def test_insufficient_all_budgets_not_scalarized_away(self):
        expensive = GenerativeForecast("generate", 1,
                                       ResourceVector(test_calls=3, tokens=1))
        choice = choose_next_intervention(None, [expensive], self.budget,
                                          ResourcePrices(), self.rule)
        self.assertEqual(choice.action, "abstain")

    def test_zero_price_can_select_but_no_free_nonterminal(self):
        proposal = GenerativeForecast("generate", .8, ResourceVector(tokens=1))
        choice = choose_next_intervention(None, [proposal], self.budget,
                                          ResourcePrices(), self.rule)
        self.assertEqual(choice.action, "generate")
        with self.assertRaises(ValueError):
            GenerativeForecast("generate", .8, ResourceVector())
        with self.assertRaises(ValueError):
            DiagnosticForecast("test", .8, .9, ResourceVector())

    def test_invalid_proposals_and_probability(self):
        with self.assertRaises(ValueError):
            GenerativeForecast("test", .5, ResourceVector(tokens=1))
        with self.assertRaises(ValueError):
            DiagnosticForecast("repair", .5, .5, ResourceVector(test_calls=1))
        with self.assertRaises(ValueError):
            DiagnosticForecast("test", 2, .5, ResourceVector(test_calls=1))
        with self.assertRaises(ValueError):
            GenerativeForecast("repair", -1, ResourceVector(tokens=1))
        with self.assertRaises(ValueError):
            ResourceVector(gpu_seconds=float("nan"))

    def test_impossible_expected_utility_fails_closed(self):
        invalid = GenerativeForecast("generate", 1.1, ResourceVector(tokens=1))
        with self.assertRaises(ValueError):
            choose_next_intervention(None, [invalid], self.budget,
                                     self.prices, self.rule)

    def test_budget_no_diagnostic_after_test_calls_depleted(self):
        rem = ResourceVector(tokens=100, test_calls=0, wall_seconds=10)
        test = DiagnosticForecast("test", 1, 1, ResourceVector(test_calls=1))
        choice = choose_next_intervention(.5, [test], rem, self.prices, self.rule)
        self.assertEqual(choice.action, "abstain")


if __name__ == "__main__":
    unittest.main()
