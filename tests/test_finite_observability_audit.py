"""First-party falsifiers for MCEA's observational-equivalence audit.

No ground-truth label of any real code patch is consulted; theta and Y are
hypothetical latent *atoms* in a frozen model. No third-party source runs.
"""
from dataclasses import replace
import unittest

from ucode.coherent_hypothesis_search import (
    EvidenceHypothesis, initial_coherent_state, kernel_fingerprint,
    plan_coherent_evidence, record_coherent_observation,
)
from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow, Observation,
)
from ucode.finite_observability_audit import audit_latent_atom_observability
from ucode.vector_policy import ResourceVector, ResourcePrices
from ucode.voi import ReleaseRule


CAL=ConditionalProbe("cal","retrieve",ResourceVector(tokens=1))
DIAG=ConditionalProbe("diag","test",ResourceVector(test_calls=1))
BUDGET=ResourceVector(tokens=1,test_calls=1)
PRICES=ResourcePrices(tokens=.01,test_calls=.01)
RULE=ReleaseRule(max_predicted_failure=.1)


def hypotheses(cal_a=1.,cal_b=0.,diag_a=1.,diag_b=0.):
    items=[]
    for name,cal,diag in (
        ("model-A",cal_a,diag_a),("model-B",cal_b,diag_b),
    ):
        rows=[]
        for action,p1,p0,other in (
            ("cal",cal,cal,"diag"),
            ("diag",diag,1-diag,"cal"),
        ):
            for history in (
                (), (Observation(other,False),),
                (Observation(other,True),),
            ):
                rows.append(ConditionalRow(action,history,p1,p0))
        items.append(EvidenceHypothesis(name,ConditionalKernel(tuple(rows))))
    return tuple(items)


class FrozenModelAndObservabilityTests(unittest.TestCase):
    def setUp(self):
        self.hs=hypotheses()
        self.s=initial_coherent_state(.5,self.hs,(.5,.5),BUDGET)

    def audit(self,probes=(DIAG,),horizon=2,state=None,hs=None,**kw):
        return audit_latent_atom_observability(
            self.s if state is None else state,probes,
            self.hs if hs is None else hs,
            ("model-A",False),("model-B",True),
            horizon=horizon,**kw,
        )

    def test_two_opposite_interpretations_are_observationally_equivalent(self):
        r=self.audit()
        self.assertTrue(r.indistinguishable)
        self.assertIsNone(r.witness_action_id)
        self.assertEqual(r.admitted_real_tasks,0)
        # These two atoms have opposite Y but yield exactly the same
        # sign of the only affordable test, regardless of the policy.
        self.assertEqual(r.left_atom[1],False)
        self.assertEqual(r.right_atom[1],True)

    def test_calibration_action_provides_distinguishing_witness(self):
        r=self.audit(probes=(DIAG,CAL))
        self.assertFalse(r.indistinguishable)
        self.assertEqual(r.witness_action_id,"cal")
        self.assertEqual(r.witness_history,())
        self.assertEqual(r.witness_positive_likelihoods,(1.,0.))

    def test_zero_budget_and_zero_horizon_only_establish_restricted_equivalence(self):
        r0=self.audit(probes=(CAL,DIAG),horizon=0)
        self.assertTrue(r0.indistinguishable)
        self.assertEqual(r0.context_count,1)
        state=replace(self.s,budget=ResourceVector())
        blocked=self.audit(probes=(CAL,DIAG),state=state)
        self.assertTrue(blocked.indistinguishable)

    def test_observable_atom_odds_remain_invariant_under_common_likelihood(self):
        # Binary-exact 0.75/0.25 values avoid decimal complement
        # representation drift (1-0.8 is not stored identically to 0.2).
        hs=hypotheses(.75,.25,.75,.25)
        s=initial_coherent_state(.5,hs,(.5,.5),BUDGET)
        initial_odds=s.joint[0][0]/s.joint[1][1]
        r=self.audit(hs=hs,state=s)
        self.assertTrue(r.indistinguishable)
        next_state=record_coherent_observation(s,DIAG,hs,True)
        later_odds=next_state.joint[0][0]/next_state.joint[1][1]
        self.assertAlmostEqual(initial_odds,later_odds)

    def test_horizon_two_finds_delayed_discrimination_not_visible_at_one(self):
        first=ConditionalProbe("alpha","retrieve",ResourceVector(tokens=1))
        second=ConditionalProbe("beta","test",ResourceVector(test_calls=1))
        hs=[]
        for name,signal in (("model-A",0.),("model-B",1.)):
            rows=[
                ConditionalRow("alpha",(),.5,.5),
                ConditionalRow("beta",(),.5,.5),
            ]
            for sign in (False,True):
                # At root the two hypothetical atoms produce identical
                # observations. After alpha+, beta can distinguish.
                b=signal if sign else .5
                rows.append(ConditionalRow(
                    "beta",(Observation("alpha",sign),),b,b))
                rows.append(ConditionalRow(
                    "alpha",(Observation("beta",sign),),.5,.5))
            hs.append(EvidenceHypothesis(name,ConditionalKernel(tuple(rows))))
        state=initial_coherent_state(.5,tuple(hs),(.5,.5),BUDGET)
        def query(depth):
            return audit_latent_atom_observability(
                state,(first,second),tuple(hs),
                ("model-A",False),("model-B",True),horizon=depth)
        self.assertTrue(query(1).indistinguishable)
        witness=query(2)
        self.assertFalse(witness.indistinguishable)
        self.assertEqual(witness.witness_action_id,"beta")
        self.assertEqual(witness.witness_history,
                         (Observation("alpha",True),))

    def test_missing_reachable_conditional_row_fails_closed(self):
        h0=self.hs[0]
        bad=EvidenceHypothesis(
            "model-B",ConditionalKernel((
                ConditionalRow("diag",(),0.,1.),
            )))
        # A fresh state is explicitly bound to the INCOMPLETE kernel;
        # the problem is missing continuation rows, not hash drift.
        hs=(h0,bad)
        state=initial_coherent_state(.5,hs,(.5,.5),BUDGET)
        with self.assertRaisesRegex(ValueError,"missing frozen"):
            audit_latent_atom_observability(
                state,(DIAG,CAL),hs,
                ("model-A",False),("model-B",True),horizon=2)

    def test_fingerprint_stable_under_likelihood_row_permutation(self):
        kernel=self.hs[0].kernel
        other=ConditionalKernel(tuple(reversed(kernel.rows)))
        self.assertEqual(kernel_fingerprint(kernel),kernel_fingerprint(other))
        other_hs=(EvidenceHypothesis("model-A",other),self.hs[1])
        # Same semantic kernel despite row storage order is acceptable.
        self.assertTrue(self.audit(hs=other_hs).indistinguishable)

    def test_changed_kernel_same_scenario_id_is_rejected_before_planning(self):
        k=self.hs[0].kernel
        changed=ConditionalKernel((
            ConditionalRow("cal",(),.6,.6),*k.rows[1:]
        ))
        swapped=(EvidenceHypothesis("model-A",changed),self.hs[1])
        with self.assertRaisesRegex(ValueError,"fingerprint drift"):
            plan_coherent_evidence(
                self.s,(CAL,DIAG),swapped,PRICES,RULE,horizon=2)
        with self.assertRaisesRegex(ValueError,"fingerprint drift"):
            record_coherent_observation(self.s,CAL,swapped,True)
        with self.assertRaisesRegex(ValueError,"fingerprint drift"):
            self.audit(hs=swapped)

    def test_observed_posterior_retains_all_prior_kernel_fingerprints(self):
        after=record_coherent_observation(self.s,CAL,self.hs,True)
        self.assertEqual(after.kernel_fingerprints,self.s.kernel_fingerprints)
        self.assertEqual(len(after.kernel_fingerprints),2)
        with self.assertRaisesRegex(ValueError,"frozen kernel fingerprint"):
            replace(self.s,kernel_fingerprints=())
        with self.assertRaisesRegex(ValueError,"frozen kernel fingerprint"):
            replace(self.s,kernel_fingerprints=("bad","bad"))

    def test_frozen_model_ids_cannot_be_permuted_without_matching_digests(self):
        # Scenario ID order can change at call time, but the mapping to its
        # exact kernel digest must remain unchanged.
        reordered=(self.hs[1],self.hs[0])
        self.assertTrue(self.audit(hs=reordered).indistinguishable)
        fake=(EvidenceHypothesis("model-A",self.hs[1].kernel),
              EvidenceHypothesis("model-B",self.hs[0].kernel))
        with self.assertRaisesRegex(ValueError,"fingerprint drift"):
            self.audit(hs=fake)

    def test_unsupported_atoms_and_cap_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"positive current posterior"):
            zero=replace(self.s,joint=((.0,.5),(.25,.25)))
            self.audit(state=zero)
        with self.assertRaisesRegex(ValueError,"distinct typed"):
            audit_latent_atom_observability(
                self.s,(DIAG,),self.hs,
                ("model-A",False),("model-A",False),
            )
        # Force a shared non-deterministic root outcome before any
        # distinguishing action; otherwise an immediate root witness
        # legitimately finishes in just one visited context.
        ambiguous=hypotheses(.5,.5,.75,.25)
        astate=initial_coherent_state(.5,ambiguous,(.5,.5),BUDGET)
        with self.assertRaisesRegex(ValueError,"context cap"):
            self.audit(probes=(CAL,DIAG),state=astate,
                       hs=ambiguous,max_contexts=1)
        with self.assertRaisesRegex(ValueError,"horizon"):
            self.audit(horizon=5)

    def test_no_false_claim_of_true_world_statistical_oracle_certificate(self):
        r=self.audit()
        self.assertIn("FINITE_FROZEN",r.interpretation)
        self.assertFalse(hasattr(r,"independent_oracle_success"))
        self.assertFalse(hasattr(r,"real_repair_accuracy"))


if __name__=="__main__":
    unittest.main()
