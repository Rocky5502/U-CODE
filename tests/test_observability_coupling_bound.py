"""Independent probability witnesses for bounded MCEA transcript observability.

This uses authored rational probabilities, never hidden labels or a real task.
The exact two-probe transcript distribution is constructed independently
of the observability auditor and its coupling calculations.
"""
from dataclasses import replace
from fractions import Fraction as Q
from itertools import product
import unittest

from ucode.coherent_hypothesis_search import (
    EvidenceHypothesis, initial_coherent_state,
)
from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow, Observation,
)
from ucode.finite_observability_audit import audit_latent_atom_observability
from ucode.vector_policy import ResourceVector


FIRST=ConditionalProbe("a","retrieve",ResourceVector(tokens=1))
SECOND=ConditionalProbe("b","test",ResourceVector(test_calls=1))
BUDGET=ResourceVector(tokens=1,test_calls=1)


def models(pa: Q, pb: Q):
    result=[]
    for name,probability in (("A",pa),("B",pb)):
        rows=[]
        for action,other in (("a","b"),("b","a")):
            for history in ((), (Observation(other,True),),
                            (Observation(other,False),)):
                rows.append(ConditionalRow(
                    action,history,float(probability),float(probability)))
        result.append(EvidenceHypothesis(
            name,ConditionalKernel(tuple(rows))))
    return tuple(result)


def exact_transcript_tv(pa: Q,pb: Q,steps: int):
    """Brute-force exact TV for a FIXED ordered sequence of independent probes."""
    def dist(p):
        return [
            (p**sum(bits))*((1-p)**(steps-sum(bits)))
            for bits in product((0,1),repeat=steps)
        ]
    da,db=dist(pa),dist(pb)
    return sum((abs(a-b) for a,b in zip(da,db)),Q(0))/2


class SequentialCouplingBoundTests(unittest.TestCase):
    def audit(self,pa,pb,depth=2,probes=(FIRST,SECOND),state=None):
        hs=models(pa,pb)
        s=initial_coherent_state(.5,hs,(.5,.5),BUDGET) if state is None else state
        return audit_latent_atom_observability(
            s,probes,hs,("A",False),("B",True),
            horizon=depth,
        )

    def test_equivalent_atoms_cannot_reduce_two_atom_classification_error(self):
        r=self.audit(Q(1,2),Q(1,2),2)
        self.assertTrue(r.indistinguishable)
        self.assertEqual(r.maximum_shared_history_discrepancy,0.)
        self.assertEqual(r.adaptive_transcript_tv_upper_bound,0.)
        self.assertEqual(r.conditional_two_atom_error_lower_bound,.5)

    def test_single_perfect_discriminator_removes_lower_bound(self):
        r=self.audit(Q(1),Q(0),1,probes=(FIRST,))
        self.assertFalse(r.indistinguishable)
        self.assertEqual(r.maximum_shared_history_discrepancy,1.)
        self.assertEqual(r.adaptive_transcript_tv_upper_bound,1.)
        self.assertEqual(r.conditional_two_atom_error_lower_bound,0.)

    def test_one_step_bound_matches_exact_fraction_bayes_risk(self):
        p,q=Q(3,4),Q(1,4)
        r=self.audit(p,q,1,probes=(FIRST,))
        exact_tv=exact_transcript_tv(p,q,1)
        exact_error=(1-exact_tv)/2
        self.assertEqual(exact_tv,Q(1,2))
        self.assertAlmostEqual(r.adaptive_transcript_tv_upper_bound,
                               float(exact_tv))
        self.assertAlmostEqual(r.conditional_two_atom_error_lower_bound,
                               float(exact_error))

    def test_two_step_upper_bound_is_conservative_not_claimed_exact(self):
        p,q=Q(5,8),Q(3,8)
        r=self.audit(p,q,2)
        exact_tv=exact_transcript_tv(p,q,2)
        self.assertEqual(exact_tv,Q(1,4))
        self.assertGreaterEqual(r.adaptive_transcript_tv_upper_bound,
                                float(exact_tv))
        self.assertAlmostEqual(r.maximum_shared_history_discrepancy,.25)
        self.assertAlmostEqual(r.adaptive_transcript_tv_upper_bound,.5)
        self.assertAlmostEqual(r.conditional_two_atom_error_lower_bound,.25)
        # True error is 0.375, strictly above the conservative bound 0.25.
        self.assertGreater(float((1-exact_tv)/2),
                           r.conditional_two_atom_error_lower_bound)

    def test_discrepancy_grid_bound_contains_exact_independent_transcript_tv(self):
        for p,q in product((Q(1,4),Q(1,2),Q(3,4)),
                           (Q(1,4),Q(1,2),Q(3,4))):
            for depth in (0,1,2):
                with self.subTest(p=p,q=q,depth=depth):
                    r=self.audit(p,q,depth)
                    exact=exact_transcript_tv(p,q,depth)
                    self.assertLessEqual(
                        float(exact),r.adaptive_transcript_tv_upper_bound+1e-12)
                    if p==q:
                        self.assertTrue(r.indistinguishable)

    def test_conditional_pair_prior_not_unconditional_dataset_error(self):
        hs=models(Q(1,2),Q(1,2))
        s=initial_coherent_state(.5,hs,(.5,.5),BUDGET)
        asymmetric=replace(s,joint=((.1,.2),(.3,.4)))
        r=audit_latent_atom_observability(
            asymmetric,(),hs,("A",False),("B",True),horizon=0)
        self.assertAlmostEqual(r.conditional_two_atom_error_lower_bound,.2)
        self.assertEqual(r.adaptive_transcript_tv_upper_bound,0.)

    def test_error_bound_inapplicable_when_correctness_labels_agree(self):
        hs=models(Q(1),Q(0))
        s=initial_coherent_state(.5,hs,(.5,.5),BUDGET)
        r=audit_latent_atom_observability(
            s,(FIRST,),hs,("A",True),("B",True),horizon=1)
        self.assertIsNone(r.conditional_two_atom_error_lower_bound)

    def test_quantities_require_full_shared_prefix_exploration(self):
        # A root witness is not sufficient to compute the claimed
        # max-over-common-histories bound: context cap must still bite.
        hs=models(Q(5,8),Q(3,8))
        s=initial_coherent_state(.5,hs,(.5,.5),BUDGET)
        with self.assertRaisesRegex(ValueError,"context cap"):
            audit_latent_atom_observability(
                s,(FIRST,SECOND),hs,("A",False),("B",True),
                horizon=2,max_contexts=1,
            )

    def test_zero_horizon_and_exhausted_resource_do_not_claim_identification(self):
        hs=models(Q(1),Q(0))
        s=initial_coherent_state(.5,hs,(.5,.5),BUDGET)
        exhausted=replace(s,budget=ResourceVector())
        for st,h in ((s,0),(exhausted,2)):
            r=audit_latent_atom_observability(
                st,(FIRST,SECOND),hs,("A",False),("B",True),horizon=h)
            self.assertEqual(r.adaptive_transcript_tv_upper_bound,0.)
            self.assertEqual(r.conditional_two_atom_error_lower_bound,.5)


if __name__=="__main__":
    unittest.main()
