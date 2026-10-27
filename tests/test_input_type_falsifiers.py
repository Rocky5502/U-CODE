"""Reject boolean-as-number policy inputs before charging five-vector resources.

In Python bool subclasses int: without strict input checks, True can mean
one token, one test invocation, or certainty about software correctness.
No external code, model inference, or unsealed oracle is touched.
"""
import unittest

from ucode.vector_policy import (
    GenerativeForecast, ResourcePrices, ResourceVector,
    choose_next_intervention,
)
from ucode.voi import (
    DiagnosticAction, ReleaseRule, choose_diagnostic, terminal_value,
)


class BudgetAndProbabilityTypeFalsifiers(unittest.TestCase):
    def test_each_resource_dimension_rejects_boolean_quota(self):
        for key in ("tokens", "test_calls", "gpu_seconds",
                    "cpu_seconds", "wall_seconds"):
            with self.subTest(resource=key):
                with self.assertRaises(ValueError):
                    ResourceVector(**{key: True})

    def test_each_price_rejects_boolean_unit_price(self):
        for key in ("tokens", "test_calls", "gpu_seconds",
                    "cpu_seconds", "wall_seconds"):
            with self.subTest(price=key):
                with self.assertRaises(ValueError):
                    ResourcePrices(**{key: False})

    def test_boolean_generating_utility_not_truth_confidence(self):
        for value in (True, False):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    GenerativeForecast(
                        "generate", value, ResourceVector(tokens=1))

    def test_boolean_acceptability_prior_rejected(self):
        for value in (True, False):
            with self.assertRaises(ValueError):
                terminal_value(value, ReleaseRule(.1))

    def test_boolean_release_risk_threshold_not_numeric(self):
        for value in (True, False):
            with self.assertRaises(ValueError):
                ReleaseRule(value)

    def test_boolean_scalar_release_rewards_rejected(self):
        for key in ("correct_reward", "failure_penalty", "unit_cost_penalty"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    ReleaseRule(.1, **{key: True})

    def test_boolean_diagnostic_cost_rejected(self):
        with self.assertRaises(ValueError):
            DiagnosticAction("test", 1.0, 1.0, True)

    def test_boolean_sensitivity_and_specificity_rejected(self):
        for key in ("sensitivity", "specificity"):
            with self.subTest(key=key):
                params = {"sensitivity": .8, "specificity": .8}
                params[key] = True
                with self.assertRaises(ValueError):
                    DiagnosticAction("test", **params, cost=1.0)

    def test_boolean_scalar_budget_rejected(self):
        with self.assertRaises(ValueError):
            choose_diagnostic(.5, [], ReleaseRule(.1), True)

    def test_boolean_planning_prior_rejected(self):
        with self.assertRaises(ValueError):
            choose_next_intervention(
                True, [], ResourceVector(),
                ResourcePrices(), ReleaseRule(.1))

    def test_real_numeric_resource_quotas_still_allowed(self):
        v = ResourceVector(
            tokens=2, test_calls=1.0, gpu_seconds=.5,
            cpu_seconds=0.0, wall_seconds=1.2)
        self.assertTrue(v.affordable(ResourceVector(tokens=1)))

    def test_real_numeric_probability_still_allowed(self):
        self.assertAlmostEqual(terminal_value(.99, ReleaseRule(.1)), .98)


if __name__ == "__main__":
    unittest.main()
