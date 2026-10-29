"""Counterexamples for archive-aware conditional Bellman evidence value.

These are deterministic mathematical fixtures, never real code repair,
external repository execution, sealed oracle or fitted likelihood accuracy.
The independent Fraction calculation checks the policy's expected-max
mechanism without borrowing the reference planner's predictions.
"""
from fractions import Fraction
import unittest

from ucode.conditional_archive import (
    ConditionalArchiveInputs, plan_conditional_archive,
    record_conditional_archive,
)
from ucode.conditional_bes import ConditionalKernel,ConditionalRow
from ucode.matched_session import SharedSession
from ucode.optimized_search import SearchAction,SearchCandidate,SearchState
from ucode.vector_policy import ResourcePrices,ResourceVector
from ucode.voi import ReleaseRule

A,B="a"*64,"b"*64
TEST=SearchAction("verify","test",ResourceVector(test_calls=1))
BUDGET=ResourceVector(test_calls=1)
RULE=ReleaseRule(max_predicted_failure=.1)
PERFECT=ConditionalKernel((ConditionalRow("verify",(),1,0),))
USELESS=ConditionalKernel((ConditionalRow("verify",(),.5,.5),))


def session(reverse=False):
    cands=(SearchCandidate(A,"initial"),SearchCandidate(B,"initial"))
    if reverse:
        cands=tuple(reversed(cands))
    return SharedSession(
        BUDGET,SearchState(BUDGET,cands,cands[0].sha256),max_candidates=2,
    )


def inputs(*,test_price=.01,prior_a=.5,prior_b=.92,reverse=False):
    priors=((A,prior_a),(B,prior_b))
    kernels=((A,PERFECT),(B,USELESS))
    if reverse:
        priors=tuple(reversed(priors))
        kernels=tuple(reversed(kernels))
    return ConditionalArchiveInputs(
        priors=priors,kernels=kernels,
        prices=ResourcePrices(test_calls=test_price),
        rule=RULE,horizon=1,max_candidates=2,
    )


class ArchiveIncumbentBellmanTests(unittest.TestCase):
    def test_stronger_incumbent_must_survive_each_test_outcome(self):
        # B has release value 2*(23/25)-1 = 21/25.
        # A has p=1/2 and a perfect binary test. With a cost 1/100:
        # E[max(A_posterior,B)]-cost =
        # 1/2*max(1,21/25)+1/2*max(0,21/25)-1/100 = 91/100.
        incumbent=Fraction(21,25)
        independent=(Fraction(1,2)*max(Fraction(1),incumbent)+
                     Fraction(1,2)*max(Fraction(0),incumbent)-
                     Fraction(1,100))
        self.assertEqual(independent,Fraction(91,100))
        plan=plan_conditional_archive(session(),(TEST,),inputs())
        self.assertEqual(plan.decision.action_id,"verify")
        self.assertEqual(plan.decision.target_sha256,A)
        self.assertAlmostEqual(plan.baseline_stop_utility,float(incumbent))
        self.assertAlmostEqual(plan.expected_proxy_utility,float(independent))
        # State count is an implementation diagnostic; the exact expected
        # value above, not the recursion count, is the scientific invariant.
        self.assertGreaterEqual(plan.expanded_states,3)

    def test_counterexample_exposes_wrong_max_outside_expectation(self):
        # The OLD algorithm returned max(.5-.01, .84)=.84 and stopped.
        old_wrong=max(float(Fraction(1,2)-Fraction(1,100)),
                      float(Fraction(21,25)))
        new=plan_conditional_archive(session(),(TEST,),inputs())
        self.assertAlmostEqual(old_wrong,.84)
        self.assertGreater(new.expected_proxy_utility,old_wrong)
        self.assertEqual(new.decision.kind,"test")

    def test_negative_test_retains_untouched_B_release(self):
        first=plan_conditional_archive(session(),(TEST,),inputs()).decision
        updated=record_conditional_archive(
            session(),(TEST,),inputs(),first,
            reported_cost=TEST.cost,observed_positive=False)
        next_plan=plan_conditional_archive(updated,(TEST,),inputs())
        self.assertEqual(next_plan.decision.kind,"release")
        self.assertEqual(next_plan.decision.target_sha256,B)
        self.assertAlmostEqual(next_plan.baseline_stop_utility,.84)
        self.assertEqual(updated.state.remaining.test_calls,0)

    def test_positive_test_releases_newly_verified_A(self):
        first=plan_conditional_archive(session(),(TEST,),inputs()).decision
        updated=record_conditional_archive(
            session(),(TEST,),inputs(),first,
            reported_cost=TEST.cost,observed_positive=True)
        next_plan=plan_conditional_archive(updated,(TEST,),inputs())
        self.assertEqual(next_plan.decision.kind,"release")
        self.assertEqual(next_plan.decision.target_sha256,A)
        self.assertAlmostEqual(next_plan.baseline_stop_utility,1)

    def test_order_of_priors_or_archive_does_not_change_recommendation(self):
        x=plan_conditional_archive(session(),(TEST,),inputs())
        y=plan_conditional_archive(
            session(reverse=True),(TEST,),inputs(reverse=True))
        self.assertEqual(x.decision,y.decision)
        self.assertAlmostEqual(x.expected_proxy_utility,y.expected_proxy_utility)

    def test_expensive_test_is_rejected_without_charging_twice(self):
        result=plan_conditional_archive(
            session(),(TEST,),inputs(test_price=.09))
        self.assertEqual(result.decision.kind,"release")
        self.assertEqual(result.decision.target_sha256,B)
        self.assertAlmostEqual(result.expected_proxy_utility,.84)

    def test_unchanged_other_candidate_can_dominate_with_zero_test_budget(self):
        exhausted=SharedSession(
            ResourceVector(test_calls=0),
            SearchState(ResourceVector(test_calls=0),
                        (SearchCandidate(A,"initial"),SearchCandidate(B,"initial")),
                        A),max_candidates=2)
        p=plan_conditional_archive(exhausted,(TEST,),inputs())
        self.assertEqual(p.decision.kind,"release")
        self.assertEqual(p.decision.target_sha256,B)
        self.assertAlmostEqual(p.expected_proxy_utility,.84)


if __name__=="__main__":
    unittest.main()
