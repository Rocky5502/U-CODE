"""Adversarial synthetic tests for actual adaptive selection over frozen receipts."""
from dataclasses import replace
import unittest

from ucode.action_id_replay_bridge import (
    ActionBoundBook, ActionBoundResponse, replay_bound_synthetic_actions,
)
from ucode.adaptive_reference_replay import run_adaptive_synthetic_reference
from ucode.matched_session import SharedDecision
from ucode.optimized_search import SearchAction, SearchPolicy
from ucode.vector_policy import ResourceVector as RV

A, B = "a"*64, "b"*64
GEN=SearchAction("gen-1","generate",RV(tokens=2))
TEST=SearchAction("test-1","test",RV(test_calls=1))
REPAIR=SearchAction("repair-1","repair",RV(tokens=3))
CAP=RV(tokens=10,test_calls=2,cpu_seconds=2,wall_seconds=2)
HEURISTIC=SearchPolicy(depth=1,beam_width=6,max_candidates=8,
                       min_positive_tests=1,
                       action_rewards=(1.0,0.0,5.0,0.0,0.0),
                       repair_after_failure_bonus=6.0,
                       first_test_bonus=2.0,
                       diversity_bonus=0.0,
                       continue_threshold=0.1)


class AdaptiveReferencesTests(unittest.TestCase):
    def setUp(self):
        self.book=ActionBoundBook((GEN,TEST,REPAIR),(
            ActionBoundResponse("gen-1","generate",None,GEN.cost,GEN.cost,
                                produced_sha256=A),
            ActionBoundResponse("test-1","test",A,TEST.cost,TEST.cost,
                                visible_positive=True),
            ActionBoundResponse("repair-1","repair",A,REPAIR.cost,RV(tokens=2),
                                produced_sha256=B),
        ))

    def check(self, name="fixed_testing", book=None, budget=CAP, **kwargs):
        return run_adaptive_synthetic_reference(
            "SYNTHETIC_ADAPTIVE_FIXTURE",name,budget,
            self.book if book is None else book,
            baseline=HEURISTIC, **kwargs)

    def test_fixed_testing_generates_tests_and_releases(self):
        out=self.check()
        self.assertEqual(out.status,"RELEASED_PENDING_INDEPENDENT_EVALUATION")
        self.assertEqual(out.selected_action_ids,("gen-1","test-1"))
        self.assertEqual(out.released_candidate_sha256,A)
        self.assertEqual(out.session.state.remaining.tokens,8)
        self.assertEqual(out.session.state.remaining.test_calls,1)
        self.assertEqual(out.independent_oracle_labels,0)
        self.assertEqual(out.model_inferences,0)
        self.assertFalse(out.trusted_resource_meter)
        self.assertFalse(out.policy_fidelity_to_published_baselines)

    def test_same_frozen_book_two_different_adaptive_reference_selectors(self):
        fixed=self.check()
        beam=self.check("no_uncertainty_search")
        self.assertEqual(beam.status,"RELEASED_PENDING_INDEPENDENT_EVALUATION")
        self.assertEqual(beam.selected_action_ids,("gen-1","test-1"))
        self.assertEqual(beam.released_candidate_sha256,A)
        self.assertEqual(beam.initial_opportunity_sha256,fixed.initial_opportunity_sha256)
        self.assertEqual(beam.response_book_sha256,fixed.response_book_sha256)

    def test_fixed_policy_failed_test_abstains_without_repair(self):
        book=replace(self.book,responses=(
            self.book.responses[0],
            replace(self.book.responses[1],visible_positive=False),
            self.book.responses[2],
        ))
        fixed=self.check(book=book)
        self.assertEqual(fixed.status,"ABSTAINED")
        self.assertEqual(fixed.selected_action_ids,("gen-1","test-1"))
        self.assertIsNone(fixed.released_candidate_sha256)
        self.assertEqual(len(fixed.session.state.candidates),1)

    def test_uncertainty_free_beam_adapts_to_failed_public_test_with_repair(self):
        book=replace(self.book,responses=(
            self.book.responses[0],
            replace(self.book.responses[1],visible_positive=False),
            self.book.responses[2],
        ))
        fixed=self.check(book=book)
        adaptive=self.check("no_uncertainty_search",book=book)
        self.assertEqual(adaptive.status,"ABSTAINED")
        self.assertEqual(adaptive.selected_action_ids,("gen-1","test-1","repair-1"))
        self.assertNotEqual(fixed.selected_action_ids,adaptive.selected_action_ids)
        self.assertEqual(adaptive.session.state.candidates[-1].parent_sha256,A)
        self.assertEqual(adaptive.session.state.candidates[-1].sha256,B)
        self.assertEqual(adaptive.response_book_sha256,fixed.response_book_sha256)

    def test_adaptive_trace_matches_preselected_replay_ledger(self):
        adaptive=self.check("no_uncertainty_search")
        choices=tuple(SharedDecision(
            r.action_id,r.kind,r.target_sha256,r.reserved_cost
        ) for r in adaptive.session.receipts)
        choices+=(SharedDecision("release","release",A,RV()),)
        replay=replay_bound_synthetic_actions(
            "SYNTHETIC_ADAPTIVE_FIXTURE",CAP,self.book,choices)
        self.assertEqual(replay.status,adaptive.status)
        self.assertEqual(replay.session.trace_sha256,adaptive.session.trace_sha256)
        self.assertEqual(replay.released_candidate_sha256,adaptive.released_candidate_sha256)

    def test_missing_selected_frozen_response_fails_closed_not_oracle_imputed(self):
        book=replace(self.book,responses=(
            self.book.responses[0],self.book.responses[2]))
        for name in ("fixed_testing","no_uncertainty_search"):
            with self.subTest(name=name):
                result=self.check(name,book=book)
                self.assertEqual(result.status,"FROZEN_PUBLIC_RESPONSE_MISSING")
                self.assertEqual(result.selected_action_ids,("gen-1",))
                self.assertIsNone(result.released_candidate_sha256)
                self.assertEqual(result.independent_oracle_labels,0)

    def test_empty_generation_abstains_not_repeat_or_repair(self):
        book=replace(self.book,responses=(
            replace(self.book.responses[0],produced_sha256=None),
            self.book.responses[1],self.book.responses[2]))
        out=self.check(book=book)
        self.assertEqual(out.status,"ABSTAINED")
        self.assertEqual(out.selected_action_ids,("gen-1",))
        self.assertIsNone(out.released_candidate_sha256)

    def test_budget_cannot_be_bypassed_even_by_fixed_generator(self):
        out=self.check(budget=RV(tokens=1))
        self.assertEqual(out.status,"ABSTAINED")
        self.assertEqual(out.selected_action_ids,())
        self.assertEqual(out.session.state.remaining.tokens,1)

    def test_replay_cap_exhaustion_does_not_fabricate_success(self):
        out=self.check(max_steps=1)
        self.assertEqual(out.status,"MAX_STEPS_REACHED_WITHOUT_TERMINAL")
        self.assertEqual(out.selected_action_ids,("gen-1",))
        self.assertIsNone(out.released_candidate_sha256)

    def test_invalid_unqualified_real_task_rejected(self):
        with self.assertRaisesRegex(ValueError,"SYNTHETIC"):
            run_adaptive_synthetic_reference("php104","fixed_testing",CAP,self.book)
        with self.assertRaisesRegex(ValueError,"SYNTHETIC"):
            run_adaptive_synthetic_reference("","fixed_testing",CAP,self.book)

    def test_no_forged_gold_result_or_policy_registrations(self):
        with self.assertRaisesRegex(ValueError,"only three"):
            self.check("ucode_conditional_bes")
        with self.assertRaises(TypeError):
            run_adaptive_synthetic_reference(
                "SYNTHETIC_ADAPTIVE_FIXTURE","fixed_testing",CAP,self.book,
                oracle_passed=True)

    def test_wrong_search_policy_type_and_archive_cap_rejected(self):
        with self.assertRaisesRegex(TypeError,"SearchPolicy"):
            run_adaptive_synthetic_reference(
                "SYNTHETIC_ADAPTIVE_FIXTURE","no_uncertainty_search",
                CAP,self.book,baseline="unverified")
        with self.assertRaisesRegex(ValueError,"archive caps"):
            self.check(max_candidates=1)

    def test_five_resource_budget_enforcement(self):
        for budget in (RV(test_calls=0,tokens=2),
                       RV(tokens=2,test_calls=1,gpu_seconds=0.1)):
            with self.subTest(budget=budget):
                out=self.check(budget=budget)
                self.assertIn(out.status,("ABSTAINED","RELEASED_PENDING_INDEPENDENT_EVALUATION"))
                self.assertTrue(budget.affordable(out.session.reported_consumption))

    def test_order_independent_action_book_digest_and_decisions(self):
        reverse=ActionBoundBook(tuple(reversed(self.book.catalog)),
                                tuple(reversed(self.book.responses)))
        a=self.check(book=self.book)
        b=self.check(book=reverse)
        self.assertEqual(a.session.trace_sha256,b.session.trace_sha256)
        self.assertEqual(a.response_book_sha256,b.response_book_sha256)
        self.assertEqual(a.initial_opportunity_sha256,b.initial_opportunity_sha256)

    def test_immutable_run_output_is_not_a_correctness_ledger(self):
        out=self.check()
        self.assertFalse(hasattr(out,"oracle_passed"))
        self.assertFalse(hasattr(out,"confidence"))
        self.assertEqual(out.policy_name,"fixed_testing")


if __name__=="__main__":
    unittest.main()
