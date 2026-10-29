"""Exact rational independent one-step oracle for archive-preserving BES.

Reference enumerator intentionally does NOT call the U-CODE Bayes updater,
terminal_value, plan_conditional, or archive code in its calculation. It
checks a finite family of hypothetical rational probabilities, not external
software repair results or calibration.
"""
from fractions import Fraction as F
from itertools import product
import unittest

from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow,
    ConditionalState, plan_conditional,
)
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


def exact_release_utility(p):
    # Frozen risk ceiling 1/10 and symmetric utilities +1/-1.
    return 2*p-1 if 1-p <= F(1,10) and 2*p-1 > 0 else F(0)


def independent_one_step(prior, sensitivity, specificity, incumbent, price):
    """Independent enumeration in Fraction arithmetic (no U-CODE helpers)."""
    stop=max(incumbent,exact_release_utility(prior))
    positive=prior*sensitivity+(1-prior)*(1-specificity)
    negative=1-positive
    after=F(0)
    if positive:
        updated=prior*sensitivity/positive
        after+=positive*max(incumbent,exact_release_utility(updated))
    if negative:
        updated=prior*(1-sensitivity)/negative
        after+=negative*max(incumbent,exact_release_utility(updated))
    return stop,max(stop,after-price)


class IndependentArchiveOutsideOptionOracleTests(unittest.TestCase):
    def test_finite_grid_one_step_bellman_matches_independent_fraction_enumeration(self):
        probe=ConditionalProbe("test","test",ResourceVector(test_calls=1))
        budget=ResourceVector(test_calls=1)
        rule=ReleaseRule(max_predicted_failure=.1)
        cases=0
        for p,sens,spec,outside,price in product(
            (F(0),F(1,4),F(1,2),F(3,4),F(7,8),F(1)),
            (F(0),F(1,4),F(3,4),F(1)),
            (F(0),F(1,4),F(3,4),F(1)),
            (F(0),F(1,4),F(1,2),F(21,25)),
            (F(0),F(1,100),F(1,4)),
        ):
            kernel=ConditionalKernel((
                ConditionalRow("test",(),float(sens),float(1-spec)),
            ))
            # In this model, the diagnostic row stores
            # P(+ | acceptable)=sens and P(+ | unacceptable)=1-spec.
            state=ConditionalState(float(p),budget)
            planned=plan_conditional(
                state,[probe],kernel,
                ResourcePrices(test_calls=float(price)),
                rule,horizon=1,outside_option=float(outside))
            expected_stop,expected=independent_one_step(
                p,sens,spec,outside,price)
            self.assertAlmostEqual(
                planned.stop_utility,float(expected_stop),places=11)
            self.assertAlmostEqual(
                planned.expected_net_utility,float(expected),places=11)
            self.assertAlmostEqual(
                planned.expected_gain,float(expected-expected_stop),places=11)
            self.assertGreaterEqual(planned.expected_net_utility+1e-12,
                                    planned.stop_utility)
            cases+=1
        # 6 priors * 4 sensitivities * 4 specificities *
        # 4 outside incumbents * 3 prices = 1,152 exact oracle checks.
        self.assertEqual(cases,1152)

    def test_exact_expected_max_inequality_is_strict_in_switching_case(self):
        incumbent=F(21,25)
        local_expectation=F(1,2)*F(1)+F(1,2)*F(0)
        expected_branchwise=F(1,2)*max(F(1),incumbent)+F(1,2)*max(F(0),incumbent)
        self.assertGreater(expected_branchwise,max(local_expectation,incumbent))
        self.assertEqual(expected_branchwise,F(23,25))


if __name__=="__main__":
    unittest.main()
