"""Synthetic falsifiers for finite-scenario one-step robust evidence selection.

All numbers are hypothetical. A frozen finite scenario set is NOT a
confidence interval, data-derived calibration guarantee or real model outcome.
"""
from dataclasses import replace
import math
import unittest

from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow,
    ConditionalState, Observation,
)
from ucode.scenario_robust_evidence import (
    choose_scenario_robust_probe, conditional_one_step_net_gain,
)
from ucode.vector_policy import ResourceVector, ResourcePrices
from ucode.voi import ReleaseRule


def kernel(*, sensitivity, false_positive, action="test"):
    return ConditionalKernel(
        (ConditionalRow(action, (), sensitivity, false_positive),))


class RobustEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.probe = ConditionalProbe(
            "test", "test", ResourceVector(test_calls=1))
        self.rule = ReleaseRule(max_predicted_failure=0.1)
        self.prices = ResourcePrices(test_calls=0.01)
        self.state = ConditionalState(
            prior=0.5, budget=ResourceVector(test_calls=2))
        self.perfect = kernel(sensitivity=1, false_positive=0)
        self.noisy = kernel(sensitivity=.8, false_positive=.2)
        self.nearperfect = kernel(sensitivity=.95, false_positive=.05)

    def plan(self, scenarios, state=None, proposals=None):
        return choose_scenario_robust_probe(
            state or self.state,
            [self.probe] if proposals is None else proposals,
            scenarios, self.prices, self.rule)

    def test_exact_perfect_binary_evidence_gain(self):
        val = conditional_one_step_net_gain(
            self.state, self.probe, self.perfect, self.prices, self.rule)
        self.assertAlmostEqual(val, .49)

    def test_single_noisy_probe_cannot_cross_ninety_percent_gate(self):
        val = conditional_one_step_net_gain(
            self.state, self.probe, self.noisy, self.prices, self.rule)
        self.assertAlmostEqual(val, -.01)

    def test_scenario_disagreement_prevents_fragile_tool_purchase(self):
        r = self.plan([self.perfect, self.noisy])
        self.assertEqual(r.action, "abstain")
        self.assertEqual(r.assessments[0].label, "SCENARIO_SENSITIVE")
        self.assertAlmostEqual(r.assessments[0].worst_case_gain, -.01)
        self.assertAlmostEqual(r.assessments[0].best_case_gain, .49)
        self.assertEqual(r.budget_after.test_calls, 2)
        self.assertEqual(r.experimental_task_count, 0)

    def test_both_positive_scenarios_trigger_feasible_probe(self):
        r = self.plan([self.perfect, self.nearperfect])
        self.assertEqual(r.action, "test")
        self.assertEqual(r.assessments[0].label, "POSITIVE_ALL")
        self.assertGreater(r.worst_case_improvement, 0)
        self.assertEqual(r.budget_after.test_calls, 1)

    def test_completely_ineffective_scenarios_prune_probe(self):
        r = self.plan([self.noisy, self.noisy])
        self.assertEqual(r.action, "abstain")
        self.assertEqual(r.assessments[0].label, "NEGATIVE_ALL")

    def test_release_prior_returns_release_instead_of_excess_testing(self):
        state = ConditionalState(.99, ResourceVector(test_calls=2))
        r = self.plan([self.noisy], state=state)
        self.assertEqual(r.action, "release")
        self.assertAlmostEqual(r.baseline_terminal_utility, .98)

    def test_strict_one_dimension_resource_cap_blocks_probe(self):
        state = ConditionalState(.5, ResourceVector(test_calls=0))
        r = self.plan([self.perfect], state=state)
        self.assertEqual(r.action, "abstain")
        self.assertEqual(r.assessments, ())

    def test_zero_scalar_price_cannot_bypass_hard_budget(self):
        r = choose_scenario_robust_probe(
            ConditionalState(.5, ResourceVector()),
            [self.probe], [self.perfect], ResourcePrices(), self.rule)
        self.assertEqual(r.action, "abstain")

    def test_positive_one_scenario_but_absent_row_in_another_rejected(self):
        missing = ConditionalKernel(
            (ConditionalRow("other", (), 1, 0),))
        with self.assertRaisesRegex(ValueError, "missing frozen"):
            self.plan([self.perfect, missing])

    def test_chronological_history_conditions_scenario_lookup(self):
        state = ConditionalState(
            .8, ResourceVector(cpu_seconds=2),
            (Observation("a", True),))
        probe = ConditionalProbe(
            "b", "static_analysis", ResourceVector(cpu_seconds=1))
        redundant = ConditionalKernel((
            ConditionalRow("b", (Observation("a", True),), 1, 1),))
        informative = ConditionalKernel((
            ConditionalRow("b", (Observation("a", True),), .95, .05),))
        r = choose_scenario_robust_probe(
            state, [probe], [redundant, informative],
            ResourcePrices(cpu_seconds=.01), self.rule)
        self.assertEqual(r.action, "abstain")
        self.assertEqual(r.assessments[0].label, "SCENARIO_SENSITIVE")

    def test_missing_context_never_falls_back_to_independence(self):
        state = ConditionalState(.8, ResourceVector(test_calls=2),
                                 (Observation("a", True),))
        with self.assertRaisesRegex(ValueError, "missing frozen"):
            self.plan([self.perfect], state=state)

    def test_zero_probability_observation_branch_skipped(self):
        always_negative = kernel(sensitivity=0, false_positive=0)
        r = self.plan([always_negative])
        self.assertEqual(r.action, "abstain")
        self.assertTrue(math.isfinite(r.assessments[0].worst_case_gain))

    def test_rules_must_not_double_charge_action_cost(self):
        rule = replace(self.rule, unit_cost_penalty=.1)
        with self.assertRaisesRegex(ValueError, "charged once"):
            choose_scenario_robust_probe(
                self.state, [self.probe], [self.perfect],
                self.prices, rule)

    def test_duplicate_action_identifiers_refused(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.plan([self.perfect], proposals=[self.probe, self.probe])

    def test_empty_scenario_ensemble_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            self.plan([])

    def test_scenario_count_cap_is_enforced(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            choose_scenario_robust_probe(
                self.state, [self.probe], [self.perfect, self.perfect],
                self.prices, self.rule, maximum_scenarios=1)

    def test_scenario_order_changes_neither_bounds_nor_action(self):
        a = self.plan([self.perfect, self.noisy])
        b = self.plan([self.noisy, self.perfect])
        self.assertEqual(a.action, b.action)
        self.assertEqual(a.assessments[0].worst_case_gain,
                         b.assessments[0].worst_case_gain)
        self.assertEqual(a.assessments[0].best_case_gain,
                         b.assessments[0].best_case_gain)

    def test_price_floor_may_switch_robustly_positive_to_stop(self):
        high = choose_scenario_robust_probe(
            self.state, [self.probe], [self.perfect, self.nearperfect],
            ResourcePrices(test_calls=.5), self.rule)
        self.assertEqual(high.action, "abstain")

    def test_unspent_action_and_budget_are_not_mutated(self):
        original_budget = self.state.budget
        original_history = self.state.history
        self.plan([self.perfect, self.nearperfect])
        self.assertEqual(self.state.budget, original_budget)
        self.assertEqual(self.state.history, original_history)


if __name__ == "__main__":
    unittest.main()
