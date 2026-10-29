"""Cross-implementation mathematics: rational oracle vs float U-CODE kernels.

Entirely invented, small finite probability examples. Counts are tests of
algebra and bookkeeping, NEVER empirical software-repair correctness.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import unittest

from ucode.reference_math_oracles import (
    binary_update, exact_terminal, one_probe_expectation,
    exhaustive_two_probe, exhaustive_missingness_envelopes,
    formula_missingness_envelopes,
)
from ucode.voi import DiagnosticAction, ReleaseRule, value_of_diagnostic
from ucode.budgeted_belief_search import (
    EvidenceAction, plan_bounded_evidence_search,
)
from ucode.conditional_bes import (
    ConditionalKernel, ConditionalRow, ConditionalProbe,
    ConditionalState, Observation, plan_conditional,
)
from ucode.vector_policy import ResourcePrices, ResourceVector


class IndependentRationalMathematicsTests(unittest.TestCase):
    def test_martingale_marginalization_and_branch_normalization(self):
        grid = (F(0), F(1, 5), F(1, 2), F(4, 5), F(1))
        for p, se, sp in product(grid, repeat=3):
            with self.subTest(p=p, se=se, sp=sp):
                pos, neg, pp, pn = binary_update(p, se, sp)
                self.assertEqual(pos + neg, 1)
                self.assertEqual((pos*pp if pos else 0)
                                 + (neg*pn if neg else 0), p)
                self.assertIsNone(pp if not pos else None)
                self.assertIsNone(pn if not neg else None)

    def test_float_voi_agrees_with_exact_rational_oracle_across_grid(self):
        # 5^3 x 3 posterior-risk gates, including boundary/impossible signals.
        grid = (F(0), F(1, 5), F(1, 2), F(4, 5), F(1))
        gates = (F(0), F(1, 10), F(1))
        for p, se, sp, gate in product(grid, grid, grid, gates):
            with self.subTest(p=p, se=se, sp=sp, gate=gate):
                result = value_of_diagnostic(
                    float(p), DiagnosticAction("probe", float(se), float(sp), 1),
                    ReleaseRule(max_predicted_failure=float(gate)),
                )
                exact = one_probe_expectation(
                    p, se, sp, failure_gate=gate,
                )
                self.assertAlmostEqual(result.expected_terminal_value_after,
                                       float(exact), places=11)
                self.assertAlmostEqual(
                    result.gross_value_of_information,
                    float(exact - exact_terminal(p, failure_gate=gate)),
                    places=11,
                )

    def test_zero_probability_branch_is_unreachable_not_fabricated(self):
        pos, neg, pp, pn = binary_update(F(1, 2), F(0), F(1))
        self.assertEqual((pos, neg), (0, 1))
        self.assertIsNone(pp)
        self.assertEqual(pn, F(1, 2))

    def test_two_independent_probes_have_exact_57_over_200_value(self):
        # p=.5, Se=Sp=.8, cost=.01, release iff p>=.9
        exact = exhaustive_two_probe()
        self.assertEqual(exact, F(57, 200))
        a = EvidenceAction("a", "test", .8, .8, ResourceVector(test_calls=1))
        b = EvidenceAction("b", "test", .8, .8, ResourceVector(test_calls=1))
        plan = plan_bounded_evidence_search(
            .5, (a,b), ResourceVector(test_calls=2),
            ResourcePrices(test_calls=.01), ReleaseRule(.1),
            horizon=2, assume_independent_diagnostics=True)
        self.assertAlmostEqual(plan.expected_net_utility, float(exact), places=11)

    def test_first_positive_and_second_positive_posterior_is_16_over_17(self):
        p = F(1,2)
        _, _, first, _ = binary_update(p, F(4,5), F(4,5))
        _, _, second, _ = binary_update(first, F(4,5), F(4,5))
        self.assertEqual(first, F(4,5))
        self.assertEqual(second, F(16,17))
        self.assertEqual(exact_terminal(second), F(15,17))

    def test_redundant_test_has_no_second_purchase_value(self):
        self.assertEqual(exhaustive_two_probe(dependence="duplicate"), 0)
        a = ConditionalProbe("a", "test", ResourceVector(test_calls=1))
        b = ConditionalProbe("b", "test", ResourceVector(test_calls=1))
        rows = [
            ConditionalRow("a", (), .8, .2),
            ConditionalRow("b", (), .8, .2),
        ]
        for label, other in (("a","b"),("b","a")):
            for sign in (True,False):
                rows.append(ConditionalRow(
                    label, (Observation(other, sign),),
                    float(sign), float(sign)))
        plan = plan_conditional(
            ConditionalState(.5, ResourceVector(test_calls=2)),
            (a,b), ConditionalKernel(tuple(rows)),
            ResourcePrices(test_calls=.01), ReleaseRule(.1),
        )
        self.assertEqual(plan.action, "abstain")
        self.assertAlmostEqual(plan.expected_net_utility, 0.0)

    def test_posterior_gate_can_have_negative_one_step_information_gain(self):
        # Gate-constrained utility can violate the ordinary unconstrained
        # Bayes-value nonnegativity intuition. Do NOT clamp negative VOI.
        p=F(91,100)
        ev=one_probe_expectation(p,F(4,5),F(4,5))
        before=exact_terminal(p)
        self.assertLess(ev, before)
        result=value_of_diagnostic(.91, DiagnosticAction("x",.8,.8,1),
                                   ReleaseRule(.1))
        self.assertLess(result.gross_value_of_information, 0)

    def test_missingness_closed_forms_equal_full_integer_enumeration(self):
        # Includes no releases, all-unknown, known wrong-only, and mixed
        # scenarios. Enumerate all possibilities for <=8 assignments.
        for s in range(4):
            for w in range(4):
                for u in range(4):
                    for missing in range(3):
                        if s+w+u+missing == 0:
                            continue
                        with self.subTest(s=s, w=w, u=u, nonrelease=missing):
                            self.assertEqual(
                                exhaustive_missingness_envelopes(s,w,u,missing),
                                formula_missingness_envelopes(s,w,u,missing))

    def test_no_known_or_potential_release_has_undefined_wrong_release_risk(self):
        b = formula_missingness_envelopes(0,0,0,3)
        self.assertIsNone(b["conditional_wrong_release"])
        b = formula_missingness_envelopes(0,0,2,3)
        self.assertEqual(b["conditional_wrong_release"], (F(0),F(1)))

    def test_known_nonreleases_never_leave_itt_denominator(self):
        b = formula_missingness_envelopes(1,1,0,8)
        self.assertEqual(b["success"], (F(1,10),F(1,10)))
        self.assertEqual(b["coverage"], (F(1,5),F(1,5)))

    def test_fail_closed_invalid_probability_and_counts(self):
        with self.assertRaises(ValueError):
            binary_update(True, F(1,2), F(1,2))
        with self.assertRaises(ValueError):
            binary_update(F(1,2), F(11,10), F(1,2))
        with self.assertRaises(ValueError):
            formula_missingness_envelopes(0,0,0,0)
        with self.assertRaises(ValueError):
            exhaustive_missingness_envelopes(-1,1,0,2)
        with self.assertRaises(ValueError):
            exhaustive_two_probe(dependence="assume-real-agent")

if __name__ == "__main__":
    unittest.main()
