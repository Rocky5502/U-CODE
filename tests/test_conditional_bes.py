"""Synthetic checks of dependence-aware BES: NEVER real model performance."""
from dataclasses import replace
import unittest

from ucode.conditional_bes import (
    ConditionalKernel, ConditionalPlan, ConditionalProbe, ConditionalRow,
    ConditionalState, Observation, plan_conditional, record_conditional,
)
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


def kernel_for(redundant):
    """Same root marginals, different conditional relationships."""
    rows = []
    for action in ("a", "b"):
        other = "b" if action == "a" else "a"
        rows.append(ConditionalRow(action, (), .8, .2))
        for sign in (False, True):
            if redundant:
                good = bad = 1.0 if sign else 0.0
            else:
                good, bad = .8, .2
            rows.append(ConditionalRow(
                action, (Observation(other, sign),), good, bad))
    return ConditionalKernel(tuple(rows))


class ConditionalEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.a = ConditionalProbe("a", "test", ResourceVector(test_calls=1))
        self.b = ConditionalProbe("b", "static_analysis",
                                  ResourceVector(cpu_seconds=1))
        self.budget = ResourceVector(test_calls=2, cpu_seconds=2)
        self.prices = ResourcePrices(test_calls=.01, cpu_seconds=.01)
        self.rule = ReleaseRule(max_predicted_failure=.1)

    def plan(self, kernel, state=None, horizon=2, probes=None):
        return plan_conditional(
            state if state is not None else ConditionalState(.5, self.budget),
            [self.a, self.b] if probes is None else probes,
            kernel, self.prices, self.rule, horizon=horizon)

    def test_independent_history_kernel_reproduces_two_probe_option_value(self):
        result = self.plan(kernel_for(False))
        self.assertEqual(result.action, "a")
        self.assertAlmostEqual(result.expected_net_utility, .285)
        self.assertEqual(result.budget_after_first.test_calls, 1)

    def test_perfectly_redundant_test_pair_has_no_synergy(self):
        result = self.plan(kernel_for(True))
        self.assertEqual(result.action, "abstain")
        self.assertAlmostEqual(result.expected_net_utility, 0)

    def test_same_marginals_can_yield_opposite_first_action(self):
        independent = self.plan(kernel_for(False))
        redundant = self.plan(kernel_for(True))
        self.assertEqual(independent.action, "a")
        self.assertEqual(redundant.action, "abstain")

    def test_conditional_positive_does_not_double_count_redundant_evidence(self):
        k = kernel_for(True)
        state = ConditionalState(.5, self.budget)
        once = record_conditional(state, self.a, k, True)
        self.assertAlmostEqual(once.prior, .8)
        twice = record_conditional(once, self.b, k, True)
        self.assertAlmostEqual(twice.prior, .8)
        self.assertEqual(twice.budget.test_calls, 1)
        self.assertEqual(twice.budget.cpu_seconds, 1)

    def test_conditional_negative_does_not_double_count_redundant_evidence(self):
        k = kernel_for(True)
        once = record_conditional(ConditionalState(.5, self.budget),
                                  self.a, k, False)
        twice = record_conditional(once, self.b, k, False)
        self.assertAlmostEqual(once.prior, .2)
        self.assertAlmostEqual(twice.prior, .2)

    def test_independent_sequential_updates_reach_sixteen_seventeenths(self):
        k = kernel_for(False)
        once = record_conditional(ConditionalState(.5, self.budget),
                                  self.a, k, True)
        twice = record_conditional(once, self.b, k, True)
        self.assertAlmostEqual(twice.prior, 16/17)
        self.assertEqual(self.plan(k, twice).action, "release")

    def test_history_kernel_requires_exact_reachable_context(self):
        k = ConditionalKernel((ConditionalRow("a", (), .8, .2),
                               ConditionalRow("b", (), .8, .2)))
        with self.assertRaisesRegex(ValueError, "missing frozen"):
            self.plan(k)

    def test_no_silent_conditional_independence_fallback(self):
        state = record_conditional(
            ConditionalState(.5, self.budget), self.a, kernel_for(False), True)
        k = ConditionalKernel((ConditionalRow("a", (), .8, .2),
                               ConditionalRow("b", (), .8, .2)))
        with self.assertRaisesRegex(ValueError, "missing frozen"):
            self.plan(k, state, horizon=1)

    def test_reject_impossible_observation(self):
        deterministic = ConditionalKernel(
            (ConditionalRow("a", (), 1, 1),))
        with self.assertRaisesRegex(ValueError, "zero-probability negative"):
            record_conditional(ConditionalState(.5, self.budget),
                               self.a, deterministic, False)

    def test_reject_repeat_purchase(self):
        k = kernel_for(False)
        once = record_conditional(ConditionalState(.5, self.budget),
                                  self.a, k, True)
        with self.assertRaisesRegex(ValueError, "already consumed"):
            record_conditional(once, self.a, k, True)

    def test_reject_budget_deficiency_on_one_resource(self):
        with self.assertRaisesRegex(ValueError, "insufficient"):
            record_conditional(ConditionalState(
                .5, ResourceVector(test_calls=2, cpu_seconds=0)),
                self.b, kernel_for(False), True)

    def test_no_releasing_under_gate_when_further_evidence_is_irrelevant(self):
        result = self.plan(kernel_for(True))
        self.assertEqual(result.stop_utility, 0)
        self.assertEqual(result.action, "abstain")

    def test_high_prior_can_prefer_immediate_release(self):
        result = self.plan(kernel_for(True),
                           ConditionalState(.99, self.budget))
        self.assertEqual(result.action, "release")
        self.assertAlmostEqual(result.expected_net_utility, .98)

    def test_zero_price_does_not_bypass_budget(self):
        result = plan_conditional(
            ConditionalState(.5, ResourceVector(test_calls=0, cpu_seconds=0)),
            [self.a, self.b], kernel_for(False),
            ResourcePrices(), self.rule, 2)
        self.assertEqual(result.action, "abstain")

    def test_immutable_histories_enforced(self):
        with self.assertRaises(ValueError):
            ConditionalState(.5, self.budget, (Observation("a", True),
                                              Observation("a", False)))
        with self.assertRaises(ValueError):
            ConditionalRow("a", (Observation("a", True),), .8, .2)

    def test_duplicate_frozen_likelihood_rejected(self):
        row = ConditionalRow("a", (), .8, .2)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            ConditionalKernel((row, row))

    def test_reject_invalid_probability_and_result_label(self):
        with self.assertRaises(ValueError):
            ConditionalRow("a", (), .8, 1.2)
        with self.assertRaises(ValueError):
            Observation("a", 1)
        with self.assertRaises(ValueError):
            record_conditional(ConditionalState(.5, self.budget),
                               self.a, kernel_for(False), 1)

    def test_reject_history_from_unknown_probe(self):
        state = ConditionalState(.8, self.budget, (Observation("outside", True),))
        with self.assertRaisesRegex(ValueError, "outside frozen"):
            self.plan(kernel_for(False), state)

    def test_state_cap_and_horizon_bounds(self):
        with self.assertRaisesRegex(ValueError, "state cap"):
            plan_conditional(ConditionalState(.5, self.budget),
                             [self.a, self.b], kernel_for(False),
                             self.prices, self.rule, max_states=1)
        with self.assertRaisesRegex(ValueError, "horizon"):
            self.plan(kernel_for(False), horizon=5)

    def test_branchwise_outside_option_reproduces_independent_exact_value(self):
        # Independent rational arithmetic: B is an untouched archived patch
        # with terminal utility 2*(23/25)-1 = 21/25. A has p=1/2 and a
        # perfect diagnostic. Its two posterior values are 1 and 0.
        # Expected value after test = (1/2)*max(1,21/25)
        #                           + (1/2)*max(0,21/25) - 1/100
        #                           = 91/100, NOT max(1/2,21/25).
        from fractions import Fraction
        incumbent=Fraction(21,25)
        independent=(Fraction(1,2)*max(Fraction(1),incumbent)
                     +Fraction(1,2)*max(Fraction(0),incumbent)
                     -Fraction(1,100))
        self.assertEqual(independent,Fraction(91,100))
        perfect=ConditionalKernel((ConditionalRow("a",(),1,0),))
        plan=plan_conditional(
            ConditionalState(.5,ResourceVector(test_calls=1)),
            [self.a],perfect,ResourcePrices(test_calls=.01),
            self.rule,horizon=1,outside_option=float(incumbent))
        self.assertEqual(plan.action,"a")
        self.assertAlmostEqual(plan.stop_utility,.84)
        self.assertAlmostEqual(plan.expected_net_utility,float(independent))
        self.assertAlmostEqual(plan.expected_gain,.07)

    def test_outside_option_is_terminal_fallback_not_extra_reward(self):
        kernel=ConditionalKernel((ConditionalRow("a",(),1,0),))
        state=ConditionalState(.5,ResourceVector(test_calls=1))
        expensive=plan_conditional(
            state,[self.a],kernel,ResourcePrices(test_calls=.1),
            self.rule,horizon=1,outside_option=.84)
        self.assertEqual(expensive.action,"abstain")
        self.assertAlmostEqual(expensive.expected_net_utility,.84)
        self.assertAlmostEqual(expensive.expected_gain,0)
        self.assertAlmostEqual(expensive.stop_utility,.84)
        # Without the incumbent, the same evidence has net value .4,
        # and the planner should still select the candidate-specific test.
        without=plan_conditional(
            state,[self.a],kernel,ResourcePrices(test_calls=.1),
            self.rule,horizon=1)
        self.assertEqual(without.action,"a")
        self.assertAlmostEqual(without.expected_net_utility,.4)

    def test_outside_option_rejects_bool_negative_nan_and_infinity(self):
        kernel=ConditionalKernel((ConditionalRow("a",(),1,0),))
        state=ConditionalState(.5,ResourceVector(test_calls=1))
        for bad in (-.1,float("nan"),float("inf"),float("-inf"),
                    True,None,"0.8"):
            with self.subTest(bad=bad),self.assertRaisesRegex(
                    ValueError,"outside option"):
                plan_conditional(
                    state,[self.a],kernel,ResourcePrices(),
                    self.rule,horizon=1,outside_option=bad)

    def test_no_evidence_can_not_beat_stronger_incumbent(self):
        state=ConditionalState(.5,ResourceVector(test_calls=0))
        irrelevant=ConditionalKernel((ConditionalRow("a",(),.5,.5),))
        plan=plan_conditional(
            state,[self.a],irrelevant,ResourcePrices(),
            self.rule,horizon=1,outside_option=.84)
        self.assertEqual(plan.action,"abstain")
        self.assertAlmostEqual(plan.expected_net_utility,.84)

    def test_single_diagnostic_can_be_bought_without_full_joint_kernel(self):
        k = ConditionalKernel((ConditionalRow("a", (), 1, 0),))
        result = self.plan(k, horizon=2, probes=[self.a])
        self.assertEqual(result.action, "a")
        self.assertAlmostEqual(result.expected_net_utility, .49)


if __name__ == "__main__":
    unittest.main()
