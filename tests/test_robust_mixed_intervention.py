"""Synthetic evidence-versus-generation policy tests (no task execution)."""
from dataclasses import replace
import unittest

from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow,
    ConditionalState, Observation,
)
from ucode.robust_mixed_intervention import choose_evidence_vs_generation
from ucode.vector_policy import GenerativeForecast, ResourceVector, ResourcePrices
from ucode.voi import ReleaseRule


def kernel(se, fp):
    return ConditionalKernel((ConditionalRow("check", (), se, fp),))


class RobustMixedTests(unittest.TestCase):
    def setUp(self):
        self.state = ConditionalState(
            .5, ResourceVector(tokens=100, test_calls=2))
        self.check = ConditionalProbe(
            "check", "test", ResourceVector(test_calls=1))
        self.generate = GenerativeForecast(
            "generate", .2, ResourceVector(tokens=5))
        self.prices = ResourcePrices(tokens=.002, test_calls=.01)
        self.rule = ReleaseRule(max_predicted_failure=.1)
        self.good = kernel(1, 0)
        self.weak = kernel(.8, .2)
        self.neargood = kernel(.95, .05)

    def choose(self, actions=None, kernels=None, state=None, prices=None, rule=None):
        return choose_evidence_vs_generation(
            state or self.state,
            [self.check, self.generate] if actions is None else actions,
            [self.good, self.weak] if kernels is None else kernels,
            prices or self.prices, rule or self.rule)

    def test_uncertain_verification_redirects_budget_to_generation(self):
        r = self.choose()
        self.assertEqual(r.action, "generate")
        self.assertEqual(r.action_kind, "generation_or_repair")
        self.assertAlmostEqual(r.conservative_net_improvement, .19)
        self.assertEqual(r.budget_after.tokens, 95)
        self.assertEqual(r.budget_after.test_calls, 2)
        self.assertEqual(r.evidence_assessments[0].label, "SCENARIO_SENSITIVE")
        self.assertEqual(r.observed_full_task_successes, 0)

    def test_robust_good_verification_beats_generation(self):
        r = self.choose(kernels=[self.good, self.neargood])
        self.assertEqual(r.action, "check")
        self.assertEqual(r.action_kind, "diagnostic")
        self.assertGreater(r.conservative_net_improvement, .19)
        self.assertEqual(r.budget_after.test_calls, 1)
        self.assertEqual(r.budget_after.tokens, 100)

    def test_bad_test_and_bad_generator_causes_abstain(self):
        r = self.choose(
            actions=[self.check, GenerativeForecast(
                "generate", 0, ResourceVector(tokens=5))],
            kernels=[self.weak, self.weak])
        self.assertEqual(r.action, "abstain")
        self.assertEqual(r.budget_after, self.state.budget)

    def test_only_generation_does_not_need_fake_diagnostic_kernels(self):
        r = self.choose(actions=[self.generate], kernels=[])
        self.assertEqual(r.action, "generate")

    def test_only_diagnostics_requires_frozen_scenarios(self):
        with self.assertRaisesRegex(ValueError, "frozen diagnostic"):
            self.choose(actions=[self.check], kernels=[])

    def test_missing_likelihood_in_any_scenario_fails_closed(self):
        unknown = ConditionalKernel(
            (ConditionalRow("else", (), 1, 0),))
        with self.assertRaisesRegex(ValueError, "missing frozen"):
            self.choose(kernels=[self.good, unknown])

    def test_hard_test_budget_exhaustion_favors_generation(self):
        s = ConditionalState(
            .5, ResourceVector(tokens=100, test_calls=0))
        r = self.choose(state=s)
        self.assertEqual(r.action, "generate")

    def test_hard_token_budget_exhaustion_may_favor_diagnostic(self):
        s = ConditionalState(
            .5, ResourceVector(tokens=0, test_calls=2))
        r = self.choose(state=s, kernels=[self.good, self.neargood])
        self.assertEqual(r.action, "check")

    def test_cost_ranking_cannot_double_charge(self):
        rule = replace(self.rule, unit_cost_penalty=.5)
        with self.assertRaisesRegex(ValueError, "double-charge"):
            self.choose(rule=rule)

    def test_impossible_generation_forecast_above_reward_rejected(self):
        with self.assertRaisesRegex(ValueError, "theoretical reward"):
            self.choose(actions=[GenerativeForecast(
                "generate", 2, ResourceVector(tokens=5))])

    def test_unknown_forecast_type_fails(self):
        with self.assertRaises(TypeError):
            self.choose(actions=["fictitious"])

    def test_duplicate_intervention_id_fails(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.choose(actions=[self.check, self.check])

    def test_no_history_reuse_of_diagnostic(self):
        state = ConditionalState(
            .5, ResourceVector(tokens=100, test_calls=2),
            (Observation("check", True),))
        r = self.choose(state=state)
        self.assertEqual(r.action, "generate")
        self.assertEqual(r.evidence_assessments, ())

    def test_terminal_release_preserved_when_no_positive_actions(self):
        s = ConditionalState(
            .99, ResourceVector(tokens=100, test_calls=2))
        r = self.choose(state=s, kernels=[self.weak])
        self.assertEqual(r.action, "release")
        self.assertEqual(r.action_kind, "terminal")

    def test_matching_scenarios_reduce_to_nominal_one_step(self):
        once = self.choose(kernels=[self.good])
        doubled = self.choose(kernels=[self.good, self.good])
        self.assertEqual(once.action, doubled.action)
        self.assertAlmostEqual(once.conservative_net_improvement,
                               doubled.conservative_net_improvement)

    def test_fixed_forecast_is_explicitly_not_robust_generation(self):
        r = self.choose()
        self.assertIn("GENERATION_POINT_FORECAST", r.applicability)

    def test_cost_changes_can_change_action(self):
        r = self.choose(kernels=[self.good, self.neargood],
                        prices=ResourcePrices(tokens=.0, test_calls=.5))
        self.assertEqual(r.action, "generate")


if __name__ == "__main__":
    unittest.main()
