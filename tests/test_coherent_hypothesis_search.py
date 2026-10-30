"""Synthetic falsifiers for a persistent unknown evidence-reliability model.

All data are authored hypothetical probabilities. The independent oracle uses
exact Fraction arithmetic and does NOT call the implementation Bayes update,
terminal evaluator or search recursion when producing reference values.
"""
from dataclasses import replace
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import unittest

from ucode.coherent_hypothesis_search import (
    EvidenceHypothesis, CoherentBeliefState,
    initial_coherent_state, plan_coherent_evidence,
    record_coherent_observation,
)
from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow, Observation,
    ConditionalState,
)
from ucode.scenario_robust_evidence import choose_scenario_robust_probe
from ucode.vector_policy import ResourceVector, ResourcePrices
from ucode.voi import ReleaseRule


CAL = ConditionalProbe("cal","retrieve",ResourceVector(tokens=1))
DIAG = ConditionalProbe("diag","test",ResourceVector(test_calls=1))
CAP=ResourceVector(tokens=1,test_calls=1)
PRICES=ResourcePrices(tokens=.01,test_calls=.01)
RULE=ReleaseRule(max_predicted_failure=.1)


def make_hypotheses(cal0=1,cal1=0,diag0=1,diag1=0):
    """Cal identifies theta, diag is positively or negatively coded by theta.

    Within theta, calibration ignores correctness; its likelihood differs
    across scenarios. Diagnostic has opposite interpretation in scenario 2.
    Rows for both action orders are pre-frozen (no post-outcome fitting).
    """
    output=[]
    for name,cal_prob,diag_sens in (
        ("model-A",cal0,diag0),("model-B",cal1,diag1),
    ):
        rows=[]
        for action,good,bad,other in (
            ("cal",cal_prob,cal_prob,"diag"),
            ("diag",diag_sens,1-diag_sens,"cal"),
        ):
            for history in (
                (), (Observation(other,True),),
                (Observation(other,False),),
            ):
                rows.append(ConditionalRow(
                    action,history,float(good),float(bad)))
        output.append(EvidenceHypothesis(name,ConditionalKernel(tuple(rows))))
    return tuple(output)


def reference_exact(cal0,cal1,diag0,diag1,p=F(1,2),gate="all_surviving_models"):
    """Independent rational Bayes-adaptive Bellman reference.

    The same UNKNOWN model identity governs BOTH diagnostic actions.
    Exact weights are maintained jointly with correctness. Prices of
    cal/diag each equal 1/100; two resources each capped to one.
    """
    assert gate in ("all_surviving_models","mixture_only")
    # Order: theta0-Y0, theta0-Y1, theta1-Y0, theta1-Y1.
    joint=((1-p)/2,p/2,(1-p)/2,p/2)
    likelihoods={
        "cal":((cal0,cal0),(cal1,cal1)),
        "diag":((1-diag0,diag0),(1-diag1,diag1)),
    }

    def terminal(masses):
        bad=masses[0]+masses[2]
        good=masses[1]+masses[3]
        if gate=="all_surviving_models":
            for k in (0,2):
                mass=masses[k]+masses[k+1]
                if mass and masses[k]/mass>F(1,10):
                    return F(0)
        if bad>F(1,10) or good-bad<=0:
            return F(0)
        return good-bad

    @lru_cache(None)
    def dp(masses,remaining):
        best=terminal(masses)
        selected=None
        if not remaining:
            return best,selected
        for action in remaining:
            expected=F(0)
            for positive in (True,False):
                weighted=[]
                for k in (0,1):
                    bad_l,good_l=likelihoods[action][k]
                    if not positive:
                        bad_l,good_l=1-bad_l,1-good_l
                    weighted.extend((
                        masses[2*k]*bad_l,masses[2*k+1]*good_l
                    ))
                mass=sum(weighted,F(0))
                if mass:
                    post=tuple(v/mass for v in weighted)
                    expected+=mass*dp(
                        post,tuple(a for a in remaining if a!=action))[0]
            net=expected-F(1,100)
            if net>best:
                selected,best=action,net
        return best,selected
    return dp(joint,("cal","diag"))


class HypothesisCoherentEvidenceTests(unittest.TestCase):
    def state(self,hypotheses=None,p=.5,weights=(.5,.5)):
        hs=make_hypotheses() if hypotheses is None else hypotheses
        return initial_coherent_state(p,hs,weights,CAP)

    def plan(self,hypotheses=None,*,horizon=2,p=.5,gate="all_surviving_models",
             state=None,max_states=10000,probes=(CAL,DIAG)):
        hs=make_hypotheses() if hypotheses is None else hypotheses
        current=self.state(hs,p) if state is None else state
        return plan_coherent_evidence(
            current,probes,hs,PRICES,RULE,horizon=horizon,
            max_states=max_states,release_gate=gate,
        )

    def test_two_step_model_identification_creates_value_with_no_one_step_gain(self):
        hs=make_hypotheses()
        one=self.plan(hs,horizon=1)
        self.assertEqual(one.action,"abstain")
        self.assertAlmostEqual(one.expected_proxy_utility,0)
        two=self.plan(hs,horizon=2)
        self.assertEqual(two.action,"cal")
        self.assertAlmostEqual(two.expected_proxy_utility,.48)
        self.assertAlmostEqual(two.stop_utility,0)
        self.assertEqual(two.real_task_results,0)
        self.assertEqual(two.budget_after_first.tokens,0)
        self.assertEqual(two.budget_after_first.test_calls,1)

    def test_scenario_one_step_maximin_has_knowledge_of_model_interpretation(self):
        # For each scenario IN ISOLATION the inverted/perfect 'diag' tells
        # the fixed candidate truth, so a 1-step scenario-wise audit
        # reports .49. When the theta identity is actually unobserved,
        # neither sign of 'diag' alone licenses safe release.
        hs=make_hypotheses()
        historical=choose_scenario_robust_probe(
            ConditionalState(.5,CAP),
            (CAL,DIAG),tuple(h.kernel for h in hs),PRICES,RULE)
        self.assertEqual(historical.action,"diag")
        self.assertAlmostEqual(historical.worst_case_improvement,.49)
        unknown=self.plan(hs,horizon=1)
        self.assertEqual(unknown.action,"abstain")
        self.assertAlmostEqual(unknown.expected_proxy_utility,0)

    def test_observed_calibration_updates_theta_not_y(self):
        hs=make_hypotheses()
        s=record_coherent_observation(self.state(hs),CAL,hs,True)
        self.assertEqual(s.scenario_weights,(1,0))
        self.assertAlmostEqual(s.probability_acceptable,.5)
        self.assertEqual(s.budget.tokens,0)
        r=record_coherent_observation(s,DIAG,hs,True)
        self.assertAlmostEqual(r.probability_acceptable,1)
        self.assertEqual(r.budget.test_calls,0)
        self.assertEqual(self.plan(hs,state=r).action,"release")

    def test_observed_calibration_negative_identifies_other_model(self):
        hs=make_hypotheses()
        s=record_coherent_observation(self.state(hs),CAL,hs,False)
        self.assertEqual(s.scenario_weights,(0,1))
        neg=record_coherent_observation(s,DIAG,hs,False)
        self.assertAlmostEqual(neg.probability_acceptable,1)
        self.assertEqual(self.plan(hs,state=neg).action,"release")

    def test_failure_sign_never_self_promotes_to_correct_patch(self):
        hs=make_hypotheses()
        s=record_coherent_observation(self.state(hs),CAL,hs,True)
        incorrect=record_coherent_observation(s,DIAG,hs,False)
        self.assertEqual(self.plan(hs,state=incorrect).action,"abstain")

    def test_20_rational_parameter_cases_match_independent_oracle(self):
        count=0
        for cal0,cal1 in product(
            (F(1),F(3,4),F(1,2),F(1,4)),
            (F(0),F(1,4),F(1,2),F(3,4),F(1)),
        ):
            # Model-A test positively coded, model-B inverted.
            ref_value,ref_action=reference_exact(
                cal0,cal1,F(1),F(0))
            r=self.plan(make_hypotheses(cal0,cal1))
            with self.subTest(cal0=cal0,cal1=cal1):
                self.assertAlmostEqual(
                    r.expected_proxy_utility,float(ref_value),places=11)
                self.assertEqual(
                    r.action,ref_action if ref_action else "abstain")
            count+=1
        self.assertEqual(count,20)

    def test_model_weights_and_observed_signs_are_bayesian_martingale(self):
        hs=make_hypotheses(F(3,4),F(1,4))
        prior=self.state(hs)
        positive=record_coherent_observation(prior,CAL,hs,True)
        negative=record_coherent_observation(prior,CAL,hs,False)
        # In this symmetric fixture P(cal+)=.5, P(cal-)=.5.
        for i in (0,1):
            self.assertAlmostEqual(
                .5*positive.scenario_weights[i]
                +.5*negative.scenario_weights[i],
                prior.scenario_weights[i])
        self.assertAlmostEqual(
            (positive.probability_acceptable+
             negative.probability_acceptable)/2,
            prior.probability_acceptable)

    def test_mixture_only_gate_and_scenario_veto_are_distinct(self):
        # Under this joint belief the pooled posterior is .95 but one
        # still-possible scenario has only .5 correctness probability.
        hs=make_hypotheses()
        state=CoherentBeliefState(
            ("model-A","model-B"),
            ((.005,.895),(.05,.05)),CAP)
        all_gate=self.plan(hs,state=state,probes=(),gate="all_surviving_models")
        pooled=self.plan(hs,state=state,probes=(),gate="mixture_only")
        self.assertEqual(all_gate.action,"abstain")
        self.assertEqual(pooled.action,"release")
        self.assertAlmostEqual(pooled.stop_utility,.89)

    def test_known_single_model_reduces_to_standard_bayesian_probe(self):
        hs=(make_hypotheses()[0],)
        s=initial_coherent_state(.5,hs,(1,),CAP)
        p=plan_coherent_evidence(
            s,(DIAG,),hs,PRICES,RULE,horizon=1)
        self.assertEqual(p.action,"diag")
        self.assertAlmostEqual(p.expected_proxy_utility,.49)

    def test_input_probe_order_is_not_tie_break_order(self):
        hs=make_hypotheses()
        a=self.plan(hs,probes=(CAL,DIAG))
        b=self.plan(hs,probes=(DIAG,CAL))
        self.assertEqual((a.action,a.expected_proxy_utility),
                         (b.action,b.expected_proxy_utility))

    def test_hard_resource_cap_and_exhausted_action_are_respected(self):
        hs=make_hypotheses()
        s=initial_coherent_state(
            .5,hs,(.5,.5),ResourceVector(tokens=0,test_calls=1))
        result=self.plan(hs,state=s)
        self.assertEqual(result.action,"abstain")
        s2=record_coherent_observation(self.state(hs),CAL,hs,True)
        self.assertEqual(
            self.plan(hs,state=s2).action,"diag")

    def test_missing_frozen_likelihood_for_reachable_model_fails_closed(self):
        hs=make_hypotheses()
        broken=EvidenceHypothesis(
            "model-B",ConditionalKernel((
                ConditionalRow("cal",(),0,0),
            )))
        with self.assertRaisesRegex(ValueError,"missing frozen"):
            self.plan((hs[0],broken))

    def test_state_cap_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"state cap"):
            self.plan(max_states=1)

    def test_impossible_public_evidence_fails_closed(self):
        hs=make_hypotheses()
        # cal=- is impossible in a single model whose calibration
        # likelihood is identically one.
        single=(hs[0],)
        s=initial_coherent_state(.5,single,(1,),CAP)
        with self.assertRaisesRegex(ValueError,"impossible"):
            record_coherent_observation(s,CAL,single,False)

    def test_strict_hypothesis_and_probability_validation(self):
        hs=make_hypotheses()
        for weights in ((.5,),(.5,.4),(1,0),(True,.5)):
            with self.subTest(weights=weights),self.assertRaises(ValueError):
                initial_coherent_state(.5,hs,weights,CAP)
        with self.assertRaisesRegex(ValueError,"joint model-truth"):
            replace(self.state(hs),joint=((.1,.1),(.1,.1)))
        with self.assertRaisesRegex(ValueError,"distinct scenario"):
            replace(self.state(hs),scenario_ids=("model-A","model-A"))
        with self.assertRaisesRegex(ValueError,"hypothesis"):
            EvidenceHypothesis("",hs[0].kernel)

    def test_evaluator_gold_is_not_a_model_parameter(self):
        fields=set(CoherentBeliefState.__dataclass_fields__)
        self.assertFalse(fields & {"gold","oracle","test_gold","correct_patch"})
        self.assertEqual(self.plan().interpretation,
                         "FINITE_SYNTHETIC_HYPOTHESIS_BAYES_NOT_CALIBRATED")

    def test_invalid_horizon_duplicate_action_and_scalar_penalty(self):
        hs=make_hypotheses()
        with self.assertRaisesRegex(ValueError,"horizon"):
            self.plan(hs,horizon=0)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.plan(hs,probes=(DIAG,DIAG))
        with self.assertRaisesRegex(ValueError,"duplicate scalar"):
            plan_coherent_evidence(
                self.state(hs),(CAL,DIAG),hs,PRICES,
                replace(RULE,unit_cost_penalty=1),
            )

    def test_unknown_gate_and_unmatched_hypothesis_ids(self):
        hs=make_hypotheses()
        with self.assertRaisesRegex(ValueError,"release gate"):
            self.plan(hs,gate="secret_certified")
        other=EvidenceHypothesis("unknown",hs[0].kernel)
        with self.assertRaisesRegex(ValueError,"identities"):
            self.plan((other,hs[1]),state=self.state(hs))


if __name__ == "__main__":
    unittest.main()
