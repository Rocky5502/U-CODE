"""Synthetic falsification checks for joint diagnostic AND generative uncertainty.

All scenarios are hypothetical, not fitted real task results. The one-step
minimax here cannot be described as multi-step joint robust POMDP optimality.
"""
from dataclasses import replace
import unittest

from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow,
    ConditionalState, Observation,
)
from ucode.joint_scenario_action import (
    FrozenJointScenario, ScenarioGenerationAction,
    ScenarioGenerationValue, choose_joint_scenario_action,
)
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


class JointScenarioOneStepTests(unittest.TestCase):
    def setUp(self):
        self.state = ConditionalState(
            .5, ResourceVector(tokens=100, test_calls=2))
        self.check = ConditionalProbe(
            "test_1", "test", ResourceVector(test_calls=1))
        self.gen = ScenarioGenerationAction(
            "generate", ResourceVector(tokens=5))
        self.rule = ReleaseRule(max_predicted_failure=.1)
        self.prices = ResourcePrices(tokens=.002, test_calls=.01)

    def scenario(self, name, sensitivity=1., fp=0., gen_value=.2):
        kernel = ConditionalKernel((
            ConditionalRow("test_1", (), sensitivity, fp),))
        return FrozenJointScenario(
            name, kernel, (
                ScenarioGenerationValue("generate", gen_value),))

    def choose(self, *scenarios, state=None, actions=None):
        return choose_joint_scenario_action(
            self.state if state is None else state,
            [self.check, self.gen] if actions is None else actions,
            scenarios, self.prices, self.rule)

    def test_both_action_types_are_ranked_under_same_frozen_scenarios(self):
        r = self.choose(self.scenario("good", 1, 0, .2),
                        self.scenario("weak", .8, .2, .25))
        self.assertEqual(r.action, "generate")
        self.assertEqual(r.category, "generation_or_repair")
        self.assertAlmostEqual(r.worst_case_net_gain, .19)
        self.assertEqual(r.remaining_budget.tokens, 95)
        self.assertEqual(r.remaining_budget.test_calls, 2)
        self.assertEqual(len(r.considered), 2)
        self.assertEqual(r.considered[0].sensitivity, "MODEL_SENSITIVE")
        self.assertEqual(r.considered[1].sensitivity, "POSITIVE_ALL")
        self.assertEqual(r.executable_task_results, 0)

    def test_well_supported_probe_can_beat_uncertain_generator(self):
        r = self.choose(self.scenario("good", 1, 0, .8),
                        self.scenario("other", .95, .05, .01))
        self.assertEqual(r.action, "test_1")
        self.assertEqual(r.category, "diagnostic")
        self.assertEqual(r.remaining_budget.test_calls, 1)
        self.assertEqual(r.remaining_budget.tokens, 100)

    def test_both_inaccurate_diagnostic_and_generator_abstain(self):
        r = self.choose(self.scenario("weak", .8, .2, .1),
                        self.scenario("bad", .8, .2, 0.))
        self.assertEqual(r.action, "abstain")
        self.assertEqual(r.category, "terminal")

    def test_missing_generation_scenario_fails_not_silent(self):
        a = self.scenario("first", 1, 0, .2)
        b = FrozenJointScenario(
            "second",
            ConditionalKernel((ConditionalRow("test_1", (), 1, 0),)),
            ())
        with self.assertRaisesRegex(ValueError, "missing frozen generation"):
            self.choose(a, b)

    def test_missing_diagnostic_scenario_fails_not_silent(self):
        s = FrozenJointScenario(
            "nodiag", None,
            (ScenarioGenerationValue("generate", .5),))
        with self.assertRaisesRegex(ValueError, "missing frozen diagnostic"):
            self.choose(s)

    def test_no_diagnostics_does_not_require_kernel(self):
        s = FrozenJointScenario(
            "only_generate", None,
            (ScenarioGenerationValue("generate", .5),))
        r = self.choose(s, actions=[self.gen])
        self.assertEqual(r.action, "generate")

    def test_no_generation_does_not_require_generation_forecast(self):
        s = FrozenJointScenario(
            "only_tests",
            ConditionalKernel((ConditionalRow("test_1", (), 1, 0),)),
            ())
        r = self.choose(s, actions=[self.check])
        self.assertEqual(r.action, "test_1")

    def test_scenario_order_does_not_change_minimax_selection(self):
        good, weak = self.scenario("good", 1, 0, .2), self.scenario("weak", .8, .2, .25)
        a = self.choose(good, weak)
        b = self.choose(weak, good)
        self.assertEqual(a.action, b.action)
        self.assertAlmostEqual(a.worst_case_net_gain, b.worst_case_net_gain)

    def test_duplicate_scenario_name_fails(self):
        s = self.scenario("same")
        with self.assertRaisesRegex(ValueError, "duplicate scenario"):
            self.choose(s, s)

    def test_empty_scenarios_fail(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            self.choose()

    def test_generator_forecast_above_max_reward_fails(self):
        with self.assertRaisesRegex(ValueError, "reward ceiling"):
            self.choose(self.scenario("excess", 1, 0, 1.5))

    def test_forged_gold_outcome_fields_are_not_supported(self):
        with self.assertRaises(TypeError):
            self.choose(
                {"gold_patch": "secret", "oracle_success": True})

    def test_negative_or_nan_forecast_rejected(self):
        for value in (-.1, float("nan"), float("inf"), True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ScenarioGenerationValue("generate", value)

    def test_duplicate_generator_forecast_per_scenario_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate generator"):
            FrozenJointScenario(
                "a", None, (
                    ScenarioGenerationValue("generate", .1),
                    ScenarioGenerationValue("generate", .2)))

    def test_zero_test_quota_prevents_probe_even_with_best_diagnostic(self):
        state = ConditionalState(.5, ResourceVector(tokens=100))
        r = self.choose(self.scenario("good", 1, 0, .2), state=state)
        self.assertEqual(r.action, "generate")

    def test_zero_token_quota_blocks_generation_even_if_optimal(self):
        state = ConditionalState(.5, ResourceVector(test_calls=2))
        r = self.choose(self.scenario("good", 1, 0, .99), state=state)
        self.assertEqual(r.action, "test_1")

    def test_missing_observed_history_context_fails(self):
        state = ConditionalState(
            .8, ResourceVector(test_calls=2),
            (Observation("earlier", True),))
        with self.assertRaisesRegex(ValueError, "missing frozen"):
            self.choose(self.scenario("good"), state=state, actions=[self.check])

    def test_rule_scalar_penalty_cannot_double_charge(self):
        with self.assertRaisesRegex(ValueError, "duplicated"):
            choose_joint_scenario_action(
                self.state, [self.check], [self.scenario("good")],
                self.prices, replace(self.rule, unit_cost_penalty=.1))

    def test_no_mutation_of_state_and_cost_budget(self):
        initial = self.state.budget
        self.choose(self.scenario("good"), self.scenario("weak", .8, .2))
        self.assertEqual(self.state.budget, initial)

    def test_repair_action_supported_separately_from_generate(self):
        repair = ScenarioGenerationAction("repair", ResourceVector(tokens=1))
        s = FrozenJointScenario(
            "repair_only", None,
            (ScenarioGenerationValue("repair", .3),))
        r = self.choose(s, actions=[repair])
        self.assertEqual(r.action, "repair")
        self.assertEqual(r.remaining_budget.tokens, 99)


if __name__ == "__main__":
    unittest.main()
