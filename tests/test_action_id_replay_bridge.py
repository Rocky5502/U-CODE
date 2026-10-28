"""Synthetic proof-of-interface for unique action IDs and patch-bound replay."""
from dataclasses import replace
import unittest

from ucode.action_id_replay_bridge import (
    ActionBoundBook, ActionBoundResponse, replay_bound_synthetic_actions,
)
from ucode.matched_session import SharedDecision
from ucode.optimized_search import SearchAction
from ucode.vector_policy import ResourceVector as RV

A,B,C="a"*64,"b"*64,"c"*64
GEN=SearchAction("gen-1","generate",RV(tokens=2))
GEN2=SearchAction("gen-2","generate",RV(tokens=3))
TEST=SearchAction("check-1","test",RV(test_calls=1))
REPAIR=SearchAction("repair-1","repair",RV(tokens=4))
BUDGET=RV(tokens=12,test_calls=2,gpu_seconds=2,cpu_seconds=2,wall_seconds=2)


class ActionIDBoundReplayTests(unittest.TestCase):
    def setUp(self):
        self.responses=(
            ActionBoundResponse("gen-1","generate",None,GEN.cost,
                                RV(tokens=2),produced_sha256=A),
            ActionBoundResponse("gen-2","generate",None,GEN2.cost,
                                RV(tokens=3),produced_sha256=B),
            ActionBoundResponse("check-1","test",A,TEST.cost,
                                RV(test_calls=1),visible_positive=True),
            ActionBoundResponse("check-1","test",B,TEST.cost,
                                RV(test_calls=1),visible_positive=False),
            ActionBoundResponse("repair-1","repair",A,REPAIR.cost,
                                RV(tokens=3),produced_sha256=C),
        )
        self.book=ActionBoundBook((GEN,GEN2,TEST,REPAIR),self.responses)
        self.g1=SharedDecision("gen-1","generate",None,GEN.cost)
        self.g2=SharedDecision("gen-2","generate",None,GEN2.cost)
        self.t_a=SharedDecision("check-1","test",A,TEST.cost)
        self.t_b=SharedDecision("check-1","test",B,TEST.cost)
        self.r_a=SharedDecision("repair-1","repair",A,REPAIR.cost)
        self.release_a=SharedDecision("release","release",A,RV())
        self.release_c=SharedDecision("release","release",C,RV())
        self.abstain=SharedDecision("abstain","abstain",None,RV())

    def run_book(self,decisions=None,book=None,task="SYNTHETIC_OFFLINE",
                 budget=BUDGET):
        return replay_bound_synthetic_actions(
            task,budget,self.book if book is None else book,
            (self.g1,self.t_a,self.r_a,self.release_c) if decisions is None else decisions)

    def test_generation_test_repair_release_keeps_exact_provenance(self):
        r=self.run_book()
        self.assertEqual(r.status,"RELEASED_PENDING_INDEPENDENT_EVALUATION")
        self.assertEqual(r.released_candidate_sha256,C)
        self.assertEqual(r.chosen_action_ids,("gen-1","check-1","repair-1"))
        self.assertEqual([x.action_id for x in r.session.receipts],
                         list(r.chosen_action_ids))
        self.assertEqual([c.sha256 for c in r.session.state.candidates],[A,C])
        self.assertEqual(r.session.state.candidates[-1].parent_sha256,A)
        self.assertEqual(r.session.state.observations[0].candidate_sha256,A)
        self.assertEqual(r.session.state.remaining.tokens,7)
        self.assertEqual(r.session.state.remaining.test_calls,1)
        self.assertEqual(r.independent_correctness_labels,0)
        self.assertEqual(r.authenticated_model_calls,0)
        self.assertFalse(r.trusted_meter_attested)

    def test_same_unique_test_id_can_be_frozen_for_two_different_candidates(self):
        a=self.run_book((self.g1,self.t_a,self.release_a))
        b=self.run_book((self.g2,self.t_b,
                         SharedDecision("release","release",B,RV())))
        self.assertTrue(a.session.state.observations[0].positive)
        self.assertFalse(b.session.state.observations[0].positive)
        self.assertNotEqual(a.released_candidate_sha256,
                            b.released_candidate_sha256)
        self.assertEqual(a.response_book_sha256,b.response_book_sha256)

    def test_same_action_id_cannot_be_replayed_on_other_target(self):
        r=self.run_book((self.g1,self.g2,self.t_a,self.t_b))
        self.assertEqual(r.status,"INVALID_OR_UNAVAILABLE_ACTION_TARGET")
        self.assertEqual(r.chosen_action_ids,("gen-1","gen-2","check-1"))

    def test_wrong_candidate_receipt_cannot_substitute(self):
        book=replace(self.book,responses=tuple(x for x in self.responses
                  if not (x.action_id=="check-1" and x.target_sha256==A)))
        r=self.run_book((self.g1,self.t_a),book)
        self.assertEqual(r.status,"FROZEN_PUBLIC_RESPONSE_MISSING")
        self.assertEqual(r.chosen_action_ids,("gen-1",))
        self.assertIsNone(r.released_candidate_sha256)

    def test_unavailable_target_never_consumes_receipt(self):
        r=self.run_book((self.g1,self.t_b))
        self.assertEqual(r.status,"INVALID_OR_UNAVAILABLE_ACTION_TARGET")
        self.assertEqual(r.session.state.remaining.test_calls,2)

    def test_mismatched_action_kind_rejected_by_menu(self):
        bad=replace(self.t_a,kind="static_analysis")
        r=self.run_book((self.g1,bad))
        self.assertEqual(r.status,"INVALID_OR_UNAVAILABLE_ACTION_TARGET")

    def test_forged_cost_rejected_by_menu(self):
        bad=replace(self.g1,reserved_cost=RV(tokens=1))
        self.assertEqual(self.run_book((bad,)).status,
                         "INVALID_OR_UNAVAILABLE_ACTION_TARGET")

    def test_larger_cost_dimension_not_affordable(self):
        for bad in (RV(tokens=1), RV(test_calls=1)):
            r=self.run_book((self.g1,),budget=bad)
            self.assertEqual(r.status,"INVALID_OR_UNAVAILABLE_ACTION_TARGET")

    def test_book_must_reconcile_action_id_kind_and_reservation(self):
        for change in (
            {"action_id":"unknown"},
            {"kind":"repair"},
            {"reserved":RV(tokens=4)},
        ):
            with self.subTest(change=change),self.assertRaises(ValueError):
                changed=replace(self.responses[0],**change)
                ActionBoundBook(self.book.catalog,(changed,)+self.responses[1:])

    def test_different_candidate_same_action_id_not_duplicate_book_key(self):
        self.assertEqual(len(self.book.responses),5)
        self.assertEqual(len({r.key for r in self.book.responses}),5)
        with self.assertRaisesRegex(ValueError,"duplicate action ID"):
            ActionBoundBook(self.book.catalog,self.responses+(self.responses[0],))

    def test_catalog_must_have_unique_action_id(self):
        with self.assertRaisesRegex(ValueError,"duplicate frozen action IDs"):
            ActionBoundBook((GEN,GEN),self.responses)

    def test_receipt_cannot_carry_hidden_oracle_or_executable_gold(self):
        with self.assertRaises(TypeError):
            ActionBoundResponse("check-1","test",A,TEST.cost,TEST.cost,
                                visible_positive=True,oracle_passed=True)
        with self.assertRaisesRegex(ValueError,"oracle verdict"):
            replace(self.responses[0],visible_positive=True)
        with self.assertRaisesRegex(ValueError,"visible boolean"):
            replace(self.responses[2],visible_positive=1)
        with self.assertRaisesRegex(ValueError,"visible boolean"):
            replace(self.responses[2],produced_sha256=C)

    def test_resource_overrun_refused_before_execution(self):
        for amount in (
            RV(tokens=3),
            RV(test_calls=1),
            RV(cpu_seconds=3),
            RV(gpu_seconds=3),
            RV(wall_seconds=3),
        ):
            with self.subTest(amount=amount),self.assertRaisesRegex(ValueError,
                    "five-vector"):
                replace(self.responses[0],used=amount)

    def test_wrong_candidate_and_noncanonical_sha_rejected(self):
        with self.assertRaisesRegex(ValueError,"canonical SHA256"):
            replace(self.responses[2],target_sha256="main")
        with self.assertRaisesRegex(ValueError,"target-free"):
            replace(self.responses[0],target_sha256=A)
        with self.assertRaisesRegex(ValueError,"needs target"):
            replace(self.responses[2],target_sha256=None)

    def test_abstain_and_no_candidate_release_keep_zero_oracle_labels(self):
        r=self.run_book((self.abstain,))
        self.assertEqual(r.status,"ABSTAINED")
        self.assertEqual(r.session.receipts,())
        r=self.run_book((self.release_a,))
        self.assertEqual(r.status,"INVALID_RELEASE_CANDIDATE")
        self.assertIsNone(r.released_candidate_sha256)
        self.assertEqual(r.independent_correctness_labels,0)

    def test_terminal_must_be_last_or_rejected_before_any_work(self):
        with self.assertRaisesRegex(ValueError,"terminal must be last"):
            self.run_book((self.abstain,self.g1))
        self.assertEqual(self.run_book((self.g1,self.abstain)).status,"ABSTAINED")

    def test_noncanonical_terminal_id_cannot_create_release(self):
        bad=replace(self.release_a,action_id="generate")
        self.assertEqual(self.run_book((self.g1,bad)).status,
                         "INVALID_TERMINAL_ACTION")

    def test_book_digest_and_trace_are_catalog_order_independent(self):
        book2=ActionBoundBook(tuple(reversed(self.book.catalog)),
                              tuple(reversed(self.book.responses)))
        self.assertEqual(self.book.digest_sha256,book2.digest_sha256)
        r1=self.run_book()
        r2=self.run_book(book=book2)
        self.assertEqual(r1.response_book_sha256,r2.response_book_sha256)
        self.assertEqual(r1.session.trace_sha256,r2.session.trace_sha256)

    def test_only_explicit_synthetic_task_ids_allowed(self):
        for task in ("php104","mvdbos/php-spider","", "SYNTHETIC"):
            with self.subTest(task=task),self.assertRaisesRegex(ValueError,
                    "real/unqualified"):
                self.run_book(task=task)

    def test_no_type_confusion_or_mutable_decision_sequence(self):
        with self.assertRaisesRegex(ValueError,"immutable decision"):
            self.run_book([self.g1])
        with self.assertRaisesRegex(TypeError,"typed preselected"):
            self.run_book(("generate",))

if __name__=="__main__":
    unittest.main()
