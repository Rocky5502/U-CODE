"""Authored, hypothetical tests for exact bounded belief-tree dynamic program.

All probabilities below are made-up mathematical inputs. No benchmark tasks,
model outputs, hidden functional oracle labels or external repositories run.
"""
from dataclasses import replace
import unittest

from ucode.budgeted_belief_search import (
    BeliefPlan, CandidateAction, CandidateScenario, EvidenceAction,
    plan_bounded_evidence_search,
)
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


class BoundedEvidenceSearchTests(unittest.TestCase):
    def setUp(self):
        self.rule = ReleaseRule(max_predicted_failure=.1)
        self.budget = ResourceVector(tokens=50, test_calls=2,
                                     cpu_seconds=20, wall_seconds=30)
        self.prices = ResourcePrices(tokens=.001, test_calls=.01)
        self.a = EvidenceAction("probe-a", "test", .8, .8,
                                ResourceVector(test_calls=1))
        self.b = EvidenceAction("probe-b", "test", .8, .8,
                                ResourceVector(test_calls=1))

    def plan(self, prior, actions, *, horizon=2, **kwargs):
        return plan_bounded_evidence_search(
            prior, actions, self.budget, self.prices, self.rule,
            horizon, **kwargs)

    def test_two_complementary_probes_outperform_myopic_stopping(self):
        one = self.plan(.5, [self.a, self.b], horizon=1)
        self.assertEqual(one.first_action, "abstain")
        two = self.plan(.5, [self.a, self.b], horizon=2,
                        assume_independent_diagnostics=True)
        self.assertEqual(two.first_action, "probe-a")
        self.assertAlmostEqual(two.expected_net_utility, .285)
        self.assertAlmostEqual(two.predicted_improvement, .285)
        self.assertEqual(two.budget_after_first.test_calls, 1)
        self.assertGreater(two.states_expanded, 1)

    def test_missing_conditional_independence_declaration_fails(self):
        with self.assertRaisesRegex(ValueError, "conditional independence"):
            self.plan(.5, [self.a, self.b], horizon=2)

    def test_hard_test_budget_eliminates_two_step_synergy(self):
        budget = ResourceVector(test_calls=1)
        plan = plan_bounded_evidence_search(
            .5, [self.a, self.b], budget, self.prices, self.rule,
            2, assume_independent_diagnostics=True)
        self.assertEqual(plan.first_action, "abstain")
        self.assertEqual(plan.budget_after_first.test_calls, 1)

    def test_generation_and_then_verification_are_complementary(self):
        generation = CandidateAction(
            "gen", "generate", (CandidateScenario(1, .5),),
            ResourceVector(tokens=40))
        verification = EvidenceAction(
            "check", "test", 1, 1, ResourceVector(test_calls=1))
        one = self.plan(None, [generation, verification], horizon=1)
        self.assertEqual(one.first_action, "abstain")
        two = self.plan(None, [generation, verification], horizon=2)
        self.assertEqual(two.first_action, "gen")
        self.assertAlmostEqual(two.expected_net_utility, .45)
        self.assertEqual(two.budget_after_first.tokens, 10)

    def test_diagnostic_cannot_be_bought_without_candidate(self):
        plan = self.plan(None, [self.a], horizon=2)
        self.assertEqual(plan.first_action, "abstain")

    def test_repair_without_candidate_is_unavailable(self):
        repair = CandidateAction("repair1", "repair",
                                 (CandidateScenario(1, .99),),
                                 ResourceVector(tokens=1))
        self.assertEqual(self.plan(None, [repair]).first_action, "abstain")

    def test_direct_generating_with_high_predicted_quality_is_eligible(self):
        generation = CandidateAction("generate1", "generate",
                                     (CandidateScenario(1, .95),),
                                     ResourceVector(tokens=10))
        chosen = self.plan(None, [generation], horizon=1)
        self.assertEqual(chosen.first_action, "generate1")
        self.assertAlmostEqual(chosen.expected_net_utility, .89)

    def test_scenario_failure_preserves_existing_candidate(self):
        repair = CandidateAction(
            "fix", "repair", (CandidateScenario(.7, None),
                              CandidateScenario(.3, .99)),
            ResourceVector(tokens=1))
        plan = self.plan(.95, [repair], horizon=1)
        self.assertEqual(plan.first_action, "fix")
        self.assertAlmostEqual(plan.immediate_stop_utility, .9)
        self.assertAlmostEqual(plan.expected_net_utility, .923)

    def test_strict_gate_can_skip_negative_value_diagnostic(self):
        diagnostic = EvidenceAction("noisy", "test", .8, .8,
                                    ResourceVector(test_calls=1))
        plan = self.plan(.91, [diagnostic], horizon=1)
        self.assertEqual(plan.first_action, "release")
        self.assertAlmostEqual(plan.expected_net_utility, .82)

    def test_perfect_diagnostic_with_known_truth_is_not_purchased(self):
        p = EvidenceAction("perfect", "test", 1, 1,
                           ResourceVector(test_calls=1))
        self.assertEqual(self.plan(0, [p]).first_action, "abstain")
        self.assertEqual(self.plan(1, [p]).first_action, "release")

    def test_one_action_used_at_most_once(self):
        # A useless single probe may not create any value by being counted
        # twice, regardless of remaining horizon or test budget.
        self.assertEqual(self.plan(.5, [self.a], horizon=4).first_action,
                         "abstain")

    def test_stable_tie_break_and_order_invariance_of_value(self):
        perfect_a = EvidenceAction("one", "test", 1, 1,
                                   ResourceVector(test_calls=1))
        perfect_b = EvidenceAction("two", "test", 1, 1,
                                   ResourceVector(test_calls=1))
        a = self.plan(.5, [perfect_a, perfect_b], horizon=1)
        b = self.plan(.5, [perfect_b, perfect_a], horizon=1)
        self.assertEqual(a.first_action, "one")
        self.assertEqual(b.first_action, "two")
        self.assertAlmostEqual(a.expected_net_utility, b.expected_net_utility)

    def test_considers_multiple_resource_types_and_prices(self):
        expensive = CandidateAction("gpu", "generate",
                                    (CandidateScenario(1, .99),),
                                    ResourceVector(gpu_seconds=1))
        tiny_budget = ResourceVector(tokens=100, gpu_seconds=0)
        out = plan_bounded_evidence_search(
            None, [expensive], tiny_budget, self.prices, self.rule, 2)
        self.assertEqual(out.first_action, "abstain")
        cost = ResourcePrices(gpu_seconds=2.0)
        out = plan_bounded_evidence_search(
            None, [expensive], ResourceVector(gpu_seconds=1),
            cost, self.rule, 2)
        self.assertEqual(out.first_action, "abstain")

    def test_unreachable_positive_branch_stays_finite(self):
        p = EvidenceAction("always-negative", "test", 0, 1,
                           ResourceVector(test_calls=1))
        out = self.plan(.5, [p], horizon=2)
        self.assertEqual(out.first_action, "abstain")

    def test_traversal_guard_aborts_large_tree(self):
        with self.assertRaisesRegex(ValueError, "state cap"):
            self.plan(.5, [self.a], horizon=2, max_states=1)

    def test_reject_invalid_probabilities_and_scenario_mass(self):
        with self.assertRaises(ValueError):
            EvidenceAction("x", "test", -1, 1, ResourceVector(test_calls=1))
        with self.assertRaises(ValueError):
            CandidateScenario(2, .5)
        with self.assertRaises(ValueError):
            CandidateScenario(1, 2)
        with self.assertRaises(ValueError):
            CandidateAction("x", "generate", (CandidateScenario(.8, .5),),
                            ResourceVector(tokens=2))

    def test_reject_duplicated_actions_and_oversized_horizon(self):
        with self.assertRaisesRegex(ValueError, "duplicate action_id"):
            self.plan(.5, [self.a, self.a])
        with self.assertRaisesRegex(ValueError, "horizon"):
            self.plan(.5, [self.a], horizon=5)
        with self.assertRaisesRegex(ValueError, "ten actions"):
            self.plan(.5, [
                EvidenceAction(str(i), "test", 1, 1,
                               ResourceVector(test_calls=1))
                for i in range(11)])

    def test_vector_prices_cannot_be_doubly_charged(self):
        rule = ReleaseRule(.1, unit_cost_penalty=.5)
        with self.assertRaisesRegex(ValueError, "ResourcePrices"):
            plan_bounded_evidence_search(.5, [self.a], self.budget,
                                         self.prices, rule)

    def test_terminal_with_no_actions_is_deterministic(self):
        release = self.plan(.95, [], horizon=4)
        abstain = self.plan(None, [], horizon=2)
        self.assertEqual(release.kind, "release")
        self.assertEqual(abstain.kind, "abstain")
        self.assertEqual(release.states_expanded, 1)
        self.assertEqual(abstain.states_expanded, 1)


if __name__ == "__main__":
    unittest.main()
