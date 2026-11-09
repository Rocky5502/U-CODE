"""S04 adversarial first-party falsifiers for conditional diagnostic ordering.

All likelihoods, latent classes and rewards are fabricated mathematical
fixtures, not real oracle labels, code-repair trials or calibrated AI models.
"""
from dataclasses import asdict
from fractions import Fraction
from itertools import product
from math import isclose
import unittest

from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow, ConditionalState,
    Observation, plan_conditional, record_conditional,
)
from ucode.conditional_kernel_coherence import audit_conditional_order_coherence
from ucode.scenario_robust_evidence import (
    choose_scenario_robust_probe, conditional_one_step_net_gain,
)
from ucode.vector_policy import RESOURCE_FIELDS, ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


A = ConditionalProbe("a", "test", ResourceVector(test_calls=1))
B = ConditionalProbe("b", "static_analysis", ResourceVector(cpu_seconds=1))
BUDGET = ResourceVector(tokens=5, test_calls=2, gpu_seconds=1,
                        cpu_seconds=2, wall_seconds=3)
PRICES = ResourcePrices(test_calls=.01, cpu_seconds=.01)
RULE = ReleaseRule(max_predicted_failure=.1)


def kernel_pair(*, dependent=False, mutate=False):
    """Two-order joint law for both latent correctness classes."""
    out = [
        ConditionalRow("a", (), .8, .2),
        ConditionalRow("b", (), .8, .2),
    ]
    for action, other in (("a", "b"), ("b", "a")):
        for sign in (False, True):
            if dependent:
                good = bad = 1.0 if sign else 0.0
            else:
                good, bad = .8, .2
            if mutate and action == "b" and sign:
                good = .1
            out.append(ConditionalRow(
                action, (Observation(other, sign),), good, bad,
            ))
    return ConditionalKernel(tuple(out))


def audit(k, *, strict=True, **kwargs):
    return audit_conditional_order_coherence(
        k, ("a", "b"), require_complete=strict, **kwargs,
    )


def exact_fraction_joint(k, first, first_positive, second, second_positive,
                         acceptable):
    """Independent pure Fraction chain-rule reference; no DP reuse."""
    root = k.get(first, ())
    after = k.get(second, (Observation(first, first_positive),))
    rowkey = "positive_if_acceptable" if acceptable else "positive_if_unacceptable"
    pfirst = Fraction(str(getattr(root, rowkey)))
    psecond = Fraction(str(getattr(after, rowkey)))
    return (pfirst if first_positive else 1-pfirst) * (
        psecond if second_positive else 1-psecond
    )


class ConditionalCoherenceS04Tests(unittest.TestCase):
    def setUp(self):
        self.state = ConditionalState(.5, BUDGET)

    def test_independent_likelihoods_commute_for_all_eight_joint_cells(self):
        checked = audit(kernel_pair())
        self.assertEqual(checked.compared_event_class_cells, 8)
        self.assertEqual(checked.missing_order_event_cells, 0)
        self.assertEqual(checked.maximum_absolute_discrepancy, 0)
        self.assertEqual(checked.violations, ())
        self.assertEqual(checked.status,
                         "LOCALLY_COHERENT_TWO_ORDER_EVENTS_ONLY")
        self.assertFalse(checked.independently_authenticated_training)
        self.assertFalse(checked.statistical_calibration_proven)
        self.assertEqual(checked.qualified_executable_task_runs, 0)

    def test_perfectly_redundant_diagnostics_still_commute(self):
        k = kernel_pair(dependent=True)
        checked = audit(k)
        self.assertEqual(checked.status,
                         "LOCALLY_COHERENT_TWO_ORDER_EVENTS_ONLY")
        self.assertEqual(checked.maximum_absolute_discrepancy, 0)

    def test_one_perturbed_conditional_row_cannot_define_single_joint_law(self):
        k = kernel_pair(dependent=True, mutate=True)
        with self.assertRaisesRegex(ValueError,
                                    "incoherent conditional diagnostic order"):
            audit(k)

    def test_incoherent_report_retains_explicit_counterexample_without_gold(self):
        r = audit(kernel_pair(dependent=True, mutate=True),
                  fail_on_incoherence=False)
        self.assertEqual(r.status, "INCOHERENT_TWO_ORDER_JOINT_EVENTS")
        self.assertGreater(r.maximum_absolute_discrepancy, .1)
        self.assertTrue(r.violations)
        self.assertTrue(all(
            v.first_action == "a" and v.second_action == "b"
            and v.class_acceptable in (True, False)
            for v in r.violations
        ))
        self.assertNotIn("oracle_passed", str(asdict(r)))
        self.assertFalse(r.statistical_calibration_proven)

    def test_independent_fraction_reference_detects_mismatched_paths(self):
        for dep in (False, True):
            k = kernel_pair(dependent=dep)
            for a_positive, b_positive, acceptable in product(
                (False, True), repeat=3
            ):
                one = exact_fraction_joint(
                    k, "a", a_positive, "b", b_positive, acceptable
                )
                other = exact_fraction_joint(
                    k, "b", b_positive, "a", a_positive, acceptable
                )
                with self.subTest(dep=dep, x=a_positive, y=b_positive,
                                  class_y=acceptable):
                    self.assertEqual(one, other)
        k = kernel_pair(dependent=True, mutate=True)
        self.assertNotEqual(
            exact_fraction_joint(k, "a", True, "b", True, True),
            exact_fraction_joint(k, "b", True, "a", True, True),
        )

    def test_partial_two_order_context_does_not_get_false_coherence(self):
        k = ConditionalKernel((
            ConditionalRow("a", (), .8, .2),
            ConditionalRow("b", (), .8, .2),
        ))
        result = audit(k, strict=False)
        self.assertEqual(result.compared_event_class_cells, 0)
        self.assertEqual(result.missing_order_event_cells, 4)
        self.assertEqual(result.status, "INCOMPLETE_TWO_ORDER_COVERAGE")
        with self.assertRaisesRegex(ValueError, "incomplete conditional order"):
            audit(k)

    def test_one_missing_conditional_context_blocks_strict_validation(self):
        k = kernel_pair(dependent=False)
        rows = tuple(r for r in k.rows if not (
            r.action_id == "b"
            and r.history == (Observation("a", True),)
        ))
        with self.assertRaisesRegex(ValueError, "incomplete conditional order"):
            audit(ConditionalKernel(rows))
        r = audit(ConditionalKernel(rows), strict=False)
        self.assertGreater(r.missing_order_event_cells, 0)
        self.assertEqual(r.status, "INCOMPLETE_TWO_ORDER_COVERAGE")

    def test_root_row_outside_registered_action_set_rejected(self):
        k = ConditionalKernel((ConditionalRow("third", (), .5, .5),))
        with self.assertRaisesRegex(ValueError, "outside frozen set"):
            audit(k)

    def test_history_row_outside_registered_action_set_rejected(self):
        k = ConditionalKernel((
            ConditionalRow("a", (Observation("third", True),), .5, .5),
        ))
        with self.assertRaisesRegex(ValueError, "outside frozen set"):
            audit(k)

    def test_strict_planner_rejects_incoherent_table_before_purchase(self):
        with self.assertRaisesRegex(ValueError, "incoherent conditional"):
            plan_conditional(self.state, (A, B),
                             kernel_pair(dependent=True, mutate=True),
                             PRICES, RULE, horizon=2,
                             require_order_coherence=True)

    def test_strict_planner_rejects_missing_opposite_order(self):
        k = ConditionalKernel((
            ConditionalRow("a", (), .8, .2),
            ConditionalRow("b", (), .8, .2),
        ))
        with self.assertRaisesRegex(ValueError, "incomplete conditional order"):
            plan_conditional(self.state, (A, B), k, PRICES, RULE,
                             horizon=2, require_order_coherence=True)

    def test_strict_planner_preserves_coherent_independent_policy(self):
        ordinary = plan_conditional(self.state, (A, B), kernel_pair(),
                                    PRICES, RULE, horizon=2)
        strict = plan_conditional(self.state, (A, B), kernel_pair(),
                                  PRICES, RULE, horizon=2,
                                  require_order_coherence=True)
        self.assertEqual((ordinary.action, ordinary.expected_net_utility),
                         (strict.action, strict.expected_net_utility))

    def test_strict_planner_does_not_force_independent_diagnostics(self):
        k = kernel_pair(dependent=True)
        decision = plan_conditional(
            self.state, (A, B), k, PRICES, RULE, horizon=2,
            require_order_coherence=True,
        )
        self.assertEqual(decision.action, "abstain")

    def test_typing_and_invalid_tolerances_fail_closed(self):
        k = kernel_pair()
        for bad in (-.1, float("nan"), float("inf"), 1e-5, True):
            with self.subTest(tolerance=bad), self.assertRaises(ValueError):
                audit(k, tolerance=bad)
        for bad in (False, -1, 4, 1.5):
            with self.subTest(history=bad), self.assertRaises(ValueError):
                audit(k, max_history_length=bad)
        with self.assertRaises(TypeError):
            audit(k, require_complete="yes")
        with self.assertRaises(TypeError):
            audit(k, fail_on_incoherence="no")

    def test_duplicate_or_reserved_action_ids_fail_closed(self):
        for ids in (("a", "a"), ("a", "release"),
                    ("abstain", "a"), ("a",), tuple(str(i) for i in range(11))):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                audit_conditional_order_coherence(kernel_pair(), ids)

    def test_probe_may_not_impersonate_terminal_release_or_abstain(self):
        for name in ("release", "abstain"):
            with self.subTest(name=name), self.assertRaisesRegex(
                    ValueError, "reserved terminal"):
                ConditionalProbe(name, "test", ResourceVector(test_calls=1))

    def test_resource_type_checks_fail_before_budget_comparison(self):
        with self.assertRaisesRegex(TypeError, "five-resource cost"):
            ConditionalProbe("a", "test", {"test_calls": 1})
        with self.assertRaisesRegex(TypeError, "five-resource budget"):
            ConditionalState(.5, {"test_calls": 2})
        with self.assertRaisesRegex(TypeError, "typed conditional state"):
            plan_conditional(None, (A,), kernel_pair(), PRICES, RULE)

    def test_scenario_terminal_only_branch_must_reject_double_cost(self):
        penalty = ReleaseRule(max_predicted_failure=.1, unit_cost_penalty=.01)
        with self.assertRaisesRegex(ValueError, "charged once"):
            choose_scenario_robust_probe(
                self.state, (), (kernel_pair(),), PRICES, penalty)
        with self.assertRaisesRegex(ValueError, "charged once"):
            choose_scenario_robust_probe(
                ConditionalState(.5, ResourceVector()), (A,),
                (kernel_pair(),), PRICES, penalty)

    def test_scenario_terminal_only_branch_checks_typed_inputs(self):
        for kwargs in (
            {"state":None, "prices":PRICES, "rule":RULE},
            {"state":self.state, "prices":None, "rule":RULE},
            {"state":self.state, "prices":PRICES, "rule":None},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(
                    TypeError, "typed state"):
                choose_scenario_robust_probe(
                    kwargs["state"], (), (kernel_pair(),),
                    kwargs["prices"], kwargs["rule"],
                )

    def test_finite_scenario_regret_witness_and_hard_five_caps(self):
        perfect = ConditionalKernel((ConditionalRow("a", (), 1, 0),))
        noisy = ConditionalKernel((ConditionalRow("a", (), .8, .2),))
        # Fractions are an independently authored witness for prior 1/2.
        # Perfect: positive branch probability 1/2 and release utility 1,
        # negative branch release utility 0; cost 1/100 => gain 49/100.
        # Noisy: both posterior branches below 0.9 release gate;
        # expected terminal utility 0; cost 1/100 => loss -1/100.
        assert Fraction(1, 2) - Fraction(1, 100) == Fraction(49, 100)
        self.assertAlmostEqual(
            conditional_one_step_net_gain(self.state, A, perfect, PRICES, RULE),
            float(Fraction(49, 100)),
        )
        self.assertAlmostEqual(
            conditional_one_step_net_gain(self.state, A, noisy, PRICES, RULE),
            -float(Fraction(1, 100)),
        )
        decision = choose_scenario_robust_probe(
            self.state, (A,), (perfect, noisy), PRICES, RULE,
        )
        self.assertEqual(decision.action, "abstain")
        self.assertEqual(decision.assessments[0].label, "SCENARIO_SENSITIVE")
        self.assertAlmostEqual(decision.assessments[0].worst_case_gain, -.01)
        for dimension in RESOURCE_FIELDS:
            cost = ResourceVector(**{dimension: 1})
            probe = ConditionalProbe("a", "test", cost)
            zero_budget = ConditionalState(.5, ResourceVector())
            result = choose_scenario_robust_probe(
                zero_budget, (probe,), (perfect,), ResourcePrices(), RULE,
            )
            with self.subTest(dimension=dimension):
                self.assertEqual(result.action, "abstain")
                self.assertEqual(result.assessments, ())
                self.assertEqual(result.budget_after, zero_budget.budget)

    def test_recording_permitted_observations_preserves_declared_budget(self):
        k = kernel_pair(dependent=True)
        next_state = record_conditional(self.state, A, k, True)
        self.assertAlmostEqual(next_state.prior, .8)
        self.assertEqual(next_state.budget.test_calls, 1)
        self.assertEqual(next_state.budget.cpu_seconds, 2)
        follow = record_conditional(next_state, B, k, True)
        self.assertAlmostEqual(follow.prior, .8)
        self.assertEqual(follow.budget.cpu_seconds, 1)
        self.assertEqual(len(follow.history), 2)

    def test_no_authentication_claims_or_oracle_labels_in_audit_output(self):
        report = audit(kernel_pair(dependent=True))
        data = str(asdict(report))
        self.assertNotIn("gold_patch", data)
        self.assertNotIn("hidden_test", data)
        self.assertFalse(report.independently_authenticated_training)
        self.assertFalse(report.statistical_calibration_proven)
        self.assertEqual(report.qualified_executable_task_runs, 0)


if __name__ == "__main__":
    unittest.main()
