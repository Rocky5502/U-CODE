"""Adversarial synthetic confidence-reference tests, not real calibration."""
from dataclasses import replace
import unittest

from ucode.action_id_replay_bridge import ActionBoundBook,ActionBoundResponse
from ucode.adaptive_reference_replay import run_adaptive_synthetic_reference
from ucode.optimized_search import SearchAction
from ucode.uncertainty_only_reference import (
    SyntheticConfidenceCard, SyntheticRiskRegister,
    choose_uncertainty_only_reference,
)
from ucode.vector_policy import ResourceVector as RV

SHA="a"*64
OTHER="b"*64
GEN=SearchAction("gen","generate",RV(tokens=5))
TEST=SearchAction("test","test",RV(test_calls=1))
REPAIR=SearchAction("repair","repair",RV(tokens=3))
CAP=RV(tokens=10,test_calls=2,gpu_seconds=5,cpu_seconds=5,wall_seconds=5)


class SyntheticUncertaintyOnlyReferenceTests(unittest.TestCase):
    def setUp(self):
        self.book=ActionBoundBook((GEN,TEST,REPAIR),(
            ActionBoundResponse("gen","generate",None,GEN.cost,RV(tokens=4),
                                produced_sha256=SHA),
            ActionBoundResponse("test","test",SHA,TEST.cost,TEST.cost,
                                visible_positive=True),
            ActionBoundResponse("repair","repair",SHA,REPAIR.cost,REPAIR.cost,
                                produced_sha256=OTHER),
        ))
        self.card=SyntheticConfidenceCard(SHA,0.5,0.95,0.95)
        self.register=SyntheticRiskRegister((self.card,),0.9)

    def run_case(self,register=None,book=None,budget=CAP):
        return run_adaptive_synthetic_reference(
            "SYNTHETIC_FAKE_CONFIDENCE","uncertainty_only",budget,
            self.book if book is None else book,
            uncertainty_register=self.register if register is None else register)

    def test_positive_public_evidence_changes_uncertainty_only_release(self):
        x=self.run_case()
        self.assertEqual(x.status,"RELEASED_PENDING_INDEPENDENT_EVALUATION")
        self.assertEqual(x.selected_action_ids,("gen","test"))
        self.assertEqual(x.released_candidate_sha256,SHA)
        self.assertEqual(x.independent_oracle_labels,0)
        self.assertEqual(x.model_inferences,0)
        self.assertFalse(x.trusted_resource_meter)
        self.assertFalse(x.policy_fidelity_to_published_baselines)

    def test_negative_public_test_abstains_without_repair(self):
        bad_book=replace(self.book,responses=(
            self.book.responses[0],
            replace(self.book.responses[1],visible_positive=False),
            self.book.responses[2]))
        x=self.run_case(book=bad_book)
        self.assertEqual(x.status,"ABSTAINED")
        self.assertEqual(x.selected_action_ids,("gen","test"))
        self.assertIsNone(x.released_candidate_sha256)

    def test_high_prior_may_release_without_public_test_but_not_oracle(self):
        card=replace(self.card,prior_acceptable=0.92)
        reg=SyntheticRiskRegister((card,),0.9)
        x=self.run_case(register=reg)
        self.assertEqual(x.selected_action_ids,("gen",))
        self.assertEqual(x.status,"RELEASED_PENDING_INDEPENDENT_EVALUATION")
        self.assertEqual(x.independent_oracle_labels,0)

    def test_no_candidate_forecast_fails_closed_abstain(self):
        reg=SyntheticRiskRegister((replace(self.card,candidate_sha256=OTHER),),0.9)
        x=self.run_case(register=reg)
        self.assertEqual(x.status,"ABSTAINED")
        self.assertEqual(x.selected_action_ids,("gen",))
        self.assertEqual(x.session.state.remaining.tokens,6)

    def test_uninformative_test_never_fabricates_calibration(self):
        card=replace(self.card,test_sensitivity=0.5,test_specificity=0.5)
        x=self.run_case(register=SyntheticRiskRegister((card,),0.9))
        self.assertEqual(x.selected_action_ids,("gen","test"))
        self.assertEqual(x.status,"ABSTAINED")

    def test_missing_public_response_has_distinct_status(self):
        book=replace(self.book,responses=(
            self.book.responses[0],self.book.responses[2]))
        x=self.run_case(book=book)
        self.assertEqual(x.status,"FROZEN_PUBLIC_RESPONSE_MISSING")
        self.assertIsNone(x.released_candidate_sha256)

    def test_depleted_test_budget_abstains(self):
        x=self.run_case(budget=RV(tokens=5,test_calls=0))
        self.assertEqual(x.status,"ABSTAINED")
        self.assertEqual(x.selected_action_ids,("gen",))

    def test_invalid_probabilities_and_bool_are_rejected(self):
        for bad in (-0.1,1.01,float("nan"),float("inf"),True):
            with self.subTest(value=bad),self.assertRaises(ValueError):
                replace(self.card,prior_acceptable=bad)
            with self.subTest(value=bad),self.assertRaises(ValueError):
                replace(self.card,test_sensitivity=bad)
            with self.subTest(value=bad),self.assertRaises(ValueError):
                replace(self.register,release_min_probability=bad)

    def test_duplicate_or_untyped_cards_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            SyntheticRiskRegister((self.card,self.card))
        with self.assertRaisesRegex(ValueError,"immutable"):
            SyntheticRiskRegister([self.card])

    def test_gold_oracle_label_cannot_enter_confidence_card(self):
        with self.assertRaises(TypeError):
            SyntheticConfidenceCard(SHA,0.5,0.95,0.95,oracle_passed=True)
        with self.assertRaises(TypeError):
            self.run_case(oracle_results=[])

    def test_uncertainty_data_is_not_shared_with_uncertainty_free_baseline(self):
        with self.assertRaisesRegex(ValueError,"cannot leak"):
            run_adaptive_synthetic_reference(
                "SYNTHETIC_FAKE_CONFIDENCE","no_uncertainty_search",
                CAP,self.book,uncertainty_register=self.register)

    def test_missing_frozen_config_for_uncertainty_only_rejected(self):
        with self.assertRaisesRegex(ValueError,"needs immutable"):
            run_adaptive_synthetic_reference(
                "SYNTHETIC_FAKE_CONFIDENCE","uncertainty_only",CAP,self.book)

    def test_real_repository_task_id_rejected(self):
        with self.assertRaisesRegex(ValueError,"SYNTHETIC"):
            run_adaptive_synthetic_reference(
                "PHP104","uncertainty_only",CAP,self.book,
                uncertainty_register=self.register)

    def test_not_permitted_to_pool_multiple_correlated_test_signs(self):
        # No calibrated independence model: a second observation is not
        # interpreted as independent extra evidence by this one-test control.
        x=self.run_case()
        self.assertEqual([r.kind for r in x.session.receipts],["generate","test"])
        self.assertNotIn("repair",x.selected_action_ids)


if __name__=="__main__":
    unittest.main()
