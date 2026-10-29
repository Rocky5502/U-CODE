"""Synthetic-only conditional BES/replay integration and falsifiers."""
from dataclasses import replace
import unittest

from ucode.action_id_replay_bridge import ActionBoundBook,ActionBoundResponse
from ucode.conditional_bes import ConditionalKernel,ConditionalRow,Observation
from ucode.conditional_bes_public_replay import run_conditional_bes_synthetic_reference
from ucode.adaptive_reference_replay import run_adaptive_synthetic_reference
from ucode.uncertainty_only_reference import SyntheticConfidenceCard,SyntheticRiskRegister
from ucode.optimized_search import SearchAction
from ucode.vector_policy import ResourcePrices,ResourceVector as RV
from ucode.voi import ReleaseRule

SHA="a"*64
GEN=SearchAction("gen","generate",RV(tokens=3))
A=SearchAction("a","test",RV(test_calls=1))
B=SearchAction("b","static_analysis",RV(cpu_seconds=1))
CAP=RV(tokens=4,test_calls=2,cpu_seconds=2,wall_seconds=3)


def kernel(redundant=False):
    rows=[]
    for action,other in (("a","b"),("b","a")):
        rows.append(ConditionalRow(action,(),.8,.2))
        for sign in (True,False):
            if redundant:
                good=bad=1.0 if sign else 0.0
            else:
                good,bad=.8,.2
            rows.append(ConditionalRow(
                action,(Observation(other,sign),),good,bad))
    return ConditionalKernel(tuple(rows))


class ConditionalPublicReplayTests(unittest.TestCase):
    def setUp(self):
        self.book=ActionBoundBook((GEN,A,B),(
            ActionBoundResponse("gen","generate",None,GEN.cost,RV(tokens=2),
                                produced_sha256=SHA),
            ActionBoundResponse("a","test",SHA,A.cost,A.cost,visible_positive=True),
            ActionBoundResponse("b","static_analysis",SHA,B.cost,B.cost,
                                visible_positive=True),
        ))
        self.confidence=SyntheticRiskRegister(
            (SyntheticConfidenceCard(SHA,.5,.8,.8),),release_min_probability=.9)
        self.prices=ResourcePrices(test_calls=.01,cpu_seconds=.01)
        self.rule=ReleaseRule(max_predicted_failure=.1)

    def check(self,book=None,kernel_=None,confidence=None,**kwargs):
        return run_conditional_bes_synthetic_reference(
            "SYNTHETIC_CONDITIONAL_REPLAY",CAP,
            self.book if book is None else book,
            self.confidence if confidence is None else confidence,
            kernel() if kernel_ is None else kernel_,
            self.prices,self.rule,**kwargs)

    def test_two_positive_public_diagnostics_can_enable_release(self):
        result=self.check()
        self.assertEqual(result.status,"RELEASED_PENDING_INDEPENDENT_EVALUATION")
        self.assertEqual(result.selected_action_ids,("gen","a","b"))
        self.assertEqual(result.released_candidate_sha256,SHA)
        self.assertEqual([x.kind for x in result.session.receipts],
                         ["generate","test","static_analysis"])
        self.assertEqual(result.session.state.remaining.tokens,2)
        self.assertEqual(result.session.state.remaining.test_calls,1)
        self.assertEqual(result.session.state.remaining.cpu_seconds,1)
        self.assertEqual(result.independent_oracle_labels,0)
        self.assertEqual(result.model_inferences,0)
        self.assertFalse(result.trusted_resource_meter)
        self.assertFalse(result.policy_fidelity_to_published_baselines)
        self.assertIn("ONE_CANDIDATE",result.stage)

    def test_uncertainty_only_abstains_after_one_positive_test(self):
        baseline=run_adaptive_synthetic_reference(
            "SYNTHETIC_CONDITIONAL_REPLAY","uncertainty_only",CAP,self.book,
            uncertainty_register=self.confidence)
        conditional=self.check()
        self.assertEqual(baseline.status,"ABSTAINED")
        self.assertEqual(baseline.selected_action_ids,("gen","a"))
        self.assertEqual(conditional.selected_action_ids,("gen","a","b"))
        self.assertEqual(conditional.response_book_sha256,
                         baseline.response_book_sha256)
        self.assertEqual(conditional.initial_opportunity_sha256,
                         baseline.initial_opportunity_sha256)

    def test_redundant_second_diagnostic_does_not_justify_purchase(self):
        result=self.check(kernel_=kernel(redundant=True))
        self.assertEqual(result.status,"ABSTAINED")
        self.assertEqual(result.selected_action_ids,("gen",))
        self.assertIsNone(result.released_candidate_sha256)

    def test_negative_first_test_abstains_and_never_imports_hidden_truth(self):
        book=replace(self.book,responses=(
            self.book.responses[0],
            replace(self.book.responses[1],visible_positive=False),
            self.book.responses[2],
        ))
        result=self.check(book=book)
        self.assertEqual(result.status,"ABSTAINED")
        self.assertEqual(result.selected_action_ids,("gen","a"))
        self.assertIsNone(result.released_candidate_sha256)

    def test_zero_depth_marginal_myopic_cannot_get_two_step_value(self):
        result=self.check(horizon=1)
        self.assertEqual(result.status,"ABSTAINED")
        self.assertEqual(result.selected_action_ids,("gen",))

    def test_missing_future_context_fails_closed_no_independence_fallback(self):
        incomplete=ConditionalKernel((
            ConditionalRow("a",(),.8,.2),
            ConditionalRow("b",(),.8,.2),
        ))
        result=self.check(kernel_=incomplete)
        self.assertEqual(result.status,"FROZEN_CONDITIONAL_MODEL_INCOMPLETE")
        self.assertEqual(result.selected_action_ids,("gen",))
        self.assertIsNone(result.released_candidate_sha256)

    def test_missing_public_outcome_halts_without_making_up_test(self):
        book=replace(self.book,responses=(
            self.book.responses[0],self.book.responses[2]))
        result=self.check(book=book)
        self.assertEqual(result.status,"FROZEN_PUBLIC_RESPONSE_MISSING")
        self.assertEqual(result.selected_action_ids,("gen",))

    def test_depleted_test_calls_forces_abstention(self):
        limited=RV(tokens=4,test_calls=0,cpu_seconds=2)
        result=run_conditional_bes_synthetic_reference(
            "SYNTHETIC_CONDITIONAL_REPLAY",limited,self.book,
            self.confidence,kernel(),self.prices,self.rule)
        self.assertEqual(result.status,"ABSTAINED")
        self.assertEqual(result.selected_action_ids,("gen",))

    def test_prior_model_mismatch_abstains_without_gold_leak(self):
        other=replace(self.confidence.cards[0],candidate_sha256="f"*64)
        result=self.check(confidence=SyntheticRiskRegister((other,),.9))
        self.assertEqual(result.status,"FROZEN_BELIEF_PROFILE_MISSING")
        self.assertEqual(result.selected_action_ids,("gen",))

    def test_release_threshold_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,"release gates"):
            self.check(confidence=replace(self.confidence,
                                          release_min_probability=.8))

    def test_external_actual_task_not_authorized(self):
        with self.assertRaisesRegex(ValueError,"synthetic"):
            run_conditional_bes_synthetic_reference(
                "PHP_104",CAP,self.book,self.confidence,kernel(),
                self.prices,self.rule)

    def test_no_gold_oracle_parameter_is_accepted(self):
        with self.assertRaises(TypeError):
            self.check(gold_passed=True)

    def test_horizon_bound_rejected(self):
        with self.assertRaisesRegex(ValueError,"horizon"):
            self.check(horizon=5)

    def test_budgets_cannot_be_replaced_by_legacy_scalar(self):
        with self.assertRaises(TypeError):
            run_conditional_bes_synthetic_reference(
                "SYNTHETIC_CONDITIONAL_REPLAY",100,self.book,
                self.confidence,kernel(),self.prices,self.rule)

    def test_unmeasured_risk_claims_remain_false(self):
        result=self.check()
        self.assertFalse(result.policy_fidelity_to_published_baselines)
        self.assertEqual(result.independent_oracle_labels,0)
        self.assertEqual(result.model_inferences,0)
        self.assertNotIn("gold",str(result).lower())


if __name__=="__main__":
    unittest.main()
