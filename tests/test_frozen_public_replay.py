"""Adversarial frozen public replay; all task/model identities synthetic only."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import unittest

from ucode.blind_policy_trace import BlindAction
from ucode.experiment_contract import FrozenStudy
from ucode.frozen_public_replay import (
    FrozenPublicOutcome, SyntheticReplayBook, run_shared_frozen_replay,
)
from ucode.shadow_assignment_parity import AssignedOpportunity
from ucode.task_view_boundary import parse_agent_task_view
from ucode.vector_policy import ResourceVector as RV

ROOT = Path(__file__).resolve().parents[1]


class FrozenReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = json.loads((ROOT / "configs/confirmatory_sbse_protocol_2026-10-25.json").read_text("utf-8"))
        cls.models = tuple(p["model_ids"])
        cls.policies = tuple(p["policy_ids"])

    def setUp(self):
        spec = "SYNTHETIC task not an independently admitted real repository."
        self.view = parse_agent_task_view({
            "repository":"synthetic/fixture","base_sha":"a"*40,
            "prefixed_spec":spec,"spec_sha256":sha256(spec.encode()).hexdigest(),
        })
        self.cap = RV(tokens=25,test_calls=2,cpu_seconds=3,wall_seconds=4)
        self.gen_cap = RV(tokens=10,cpu_seconds=1,wall_seconds=1)
        self.gen_used = RV(tokens=7,cpu_seconds=1,wall_seconds=1)
        self.test_cap = RV(test_calls=1,wall_seconds=1)
        self.patch = "SYNTHETIC patch generated from immutable public fixture"
        self.patch_sha = sha256(self.patch.encode()).hexdigest()
        self.book = SyntheticReplayBook("b"*64, (
            FrozenPublicOutcome("generate",0,None,self.gen_cap,
                                self.gen_used,patch=self.patch),
            FrozenPublicOutcome("test",0,self.patch_sha,self.test_cap,
                                self.test_cap,feedback="SYNTHETIC public diagnostic"),
        ))
        self.study = FrozenStudy(
            (("SYNTHETIC_REPLAY_TASK","synthetic-lineage"),),
            self.models,self.policies,(11,),(("illustrative-budget",self.cap),))
        self.rows = tuple(AssignedOpportunity(
            task_id="SYNTHETIC_REPLAY_TASK",
            lineage_group="synthetic-lineage",model_id=model,
            policy_id=policy,seed=11,budget_id="illustrative-budget",
            pre_fix_base_sha40=self.view.base_sha,
            model_checkpoint_sha40="c"*40,
            task_spec_sha256=self.view.spec_sha256,
            public_candidate_archive_sha256="d"*64,
            common_opportunity_catalog_sha256="b"*64,
            tool_access_sha256="e"*64,
            environment_image_sha256="f"*64,
            resource_cap=self.cap,
        ) for model in self.models for policy in self.policies)
        self.pair_books = {
            ("SYNTHETIC_REPLAY_TASK",model,11,"illustrative-budget"):self.book
            for model in self.models
        }
        self.calls=[]
        def factory(row):
            self.calls.append(row.policy_id)
            def policy(st):
                if not st.history:
                    return BlindAction("generate",self.gen_cap)
                if len(st.history)==1:
                    return BlindAction("test",self.test_cap)
                return BlindAction("release",RV())
            return policy
        self.handlers={p:factory for p in self.policies}

    def run_book(self,books=None,rows=None,handlers=None,views=None):
        return run_shared_frozen_replay(
            self.study, self.rows if rows is None else rows,
            {"SYNTHETIC_REPLAY_TASK":self.view} if views is None else views,
            self.handlers if handlers is None else handlers,
            self.pair_books if books is None else books,
        )

    def test_all_eight_arms_replay_same_outcomes_without_model_or_oracle(self):
        r=self.run_book()
        self.assertEqual(r.shadow.total_shadow_arm_wirings,48)
        self.assertEqual(r.matched_contexts,6)
        self.assertEqual({x.patch_sha256 for x in r.shadow.arms},{self.patch_sha})
        self.assertEqual({x.visible_trace_sha256 for x in r.shadow.arms}.__len__(),1)
        self.assertEqual({x.terminal_status for x in r.shadow.arms},
                         {"RELEASED_PENDING_INDEPENDENT_EVALUATION"})
        self.assertEqual({x.reported_remaining.tokens for x in r.shadow.arms},{18})
        self.assertEqual(r.shadow.independent_oracle_labels,0)
        self.assertEqual(r.shadow.verified_model_inferences,0)
        self.assertFalse(r.authenticated_shared_sampling)
        self.assertEqual(r.sealed_oracle_results,0)

    def test_manifest_digest_order_independent(self):
        x=self.run_book()
        y=self.run_book(rows=tuple(reversed(self.rows)))
        self.assertEqual(x.book_manifest_sha256,y.book_manifest_sha256)
        book=replace(self.book,entries=tuple(reversed(self.book.entries)))
        self.assertEqual(self.book.digest_sha256,book.digest_sha256)

    def test_missing_pair_book_fails_before_handler_constructed(self):
        x=dict(self.pair_books)
        x.pop(next(iter(x)))
        with self.assertRaisesRegex(ValueError,"complete exact"):
            self.run_book(books=x)
        self.assertEqual(self.calls,[])

    def test_wrong_declared_catalog_fails_before_any_handler(self):
        x=dict(self.pair_books)
        key=next(iter(x))
        x[key]=replace(self.book,catalog_sha256="1"*64)
        with self.assertRaisesRegex(ValueError,"declared action catalog"):
            self.run_book(books=x)
        self.assertEqual(self.calls,[])

    def test_duplicate_action_key_rejected_at_book_construction(self):
        with self.assertRaisesRegex(ValueError,"duplicate frozen"):
            replace(self.book,entries=self.book.entries+(self.book.entries[0],))

    def test_missing_diagnostic_fails_closed_after_generated_candidate(self):
        partial=replace(self.book,entries=self.book.entries[:1])
        books={k:partial for k in self.pair_books}
        x=self.run_book(books=books)
        self.assertEqual({a.terminal_status for a in x.shadow.arms},
                         {"TOOL_FAILED_COST_UNVERIFIED"})
        self.assertTrue(all(a.patch_sha256 is None for a in x.shadow.arms))
        self.assertEqual(x.shadow.real_task_successes,0)

    def test_wrong_candidate_target_does_not_substitute_a_result(self):
        wrong=replace(self.book.entries[1],prior_patch_sha256="0"*64)
        book=replace(self.book,entries=(self.book.entries[0],wrong))
        x=self.run_book(books={k:book for k in self.pair_books})
        self.assertEqual({a.terminal_status for a in x.shadow.arms},
                         {"TOOL_FAILED_COST_UNVERIFIED"})

    def test_second_generation_without_frozen_draw_fails_closed(self):
        def factory(row):
            def policy(st):
                return BlindAction("generate",self.gen_cap)
            return policy
        x=self.run_book(handlers={p:factory for p in self.policies})
        self.assertEqual({a.terminal_status for a in x.shadow.arms},
                         {"TOOL_FAILED_COST_UNVERIFIED"})
        self.assertTrue(all(a.public_action_count==1 for a in x.shadow.arms))

    def test_mismatched_cost_reservation_fails_closed(self):
        cap=RV(tokens=11,cpu_seconds=1,wall_seconds=1)
        def factory(row):
            return lambda st: BlindAction("generate",cap)
        x=self.run_book(handlers={p:factory for p in self.policies})
        self.assertEqual({a.terminal_status for a in x.shadow.arms},
                         {"TOOL_FAILED_COST_UNVERIFIED"})

    def test_frozen_cost_cannot_exceed_reserved_cost(self):
        with self.assertRaisesRegex(ValueError,"five-resource"):
            FrozenPublicOutcome("generate",0,None,self.gen_cap,
                                RV(tokens=11),patch=self.patch)

    def test_frozen_book_rejects_non_synthetic_output_and_gold_field(self):
        with self.assertRaisesRegex(ValueError,"synthetic candidate"):
            replace(self.book.entries[0],patch="secret original gold patch")
        with self.assertRaisesRegex(ValueError,"synthetic public feedback"):
            replace(self.book.entries[1],feedback="oracle answer is true")
        with self.assertRaises(TypeError):
            FrozenPublicOutcome("test",0,self.patch_sha,self.test_cap,
                                self.test_cap,oracle_passed=True)

    def test_frozen_book_does_not_accept_wrong_types_or_unsafe_targets(self):
        with self.assertRaisesRegex(ValueError,"bounded action"):
            replace(self.book.entries[0],occurrence=True)
        with self.assertRaisesRegex(ValueError,"prior candidate"):
            replace(self.book.entries[1],prior_patch_sha256="main")
        with self.assertRaisesRegex(ValueError,"generation"):
            replace(self.book.entries[0],prior_patch_sha256=self.patch_sha)
        with self.assertRaisesRegex(ValueError,"existing candidate"):
            replace(self.book.entries[1],prior_patch_sha256=None)

    def test_abstention_does_not_consume_oracle_or_book(self):
        def factory(row):
            return lambda st: BlindAction("abstain",RV())
        x=self.run_book(handlers={p:factory for p in self.policies})
        self.assertEqual({a.terminal_status for a in x.shadow.arms},{"ABSTAINED"})
        self.assertEqual(x.shadow.real_task_successes,0)

    def test_actual_repository_is_rejected_even_with_valid_books(self):
        real=parse_agent_task_view({
            "repository":"mvdbos/php-spider",
            "base_sha":self.view.base_sha,
            "prefixed_spec":self.view.prefixed_spec,
            "spec_sha256":self.view.spec_sha256,
        })
        with self.assertRaisesRegex(ValueError,"cannot accept real"):
            self.run_book(views={"SYNTHETIC_REPLAY_TASK":real})
        self.assertEqual(self.calls,[])

    def test_missing_eight_policy_arm_blocked_before_execution(self):
        with self.assertRaisesRegex(ValueError,"incomplete"):
            self.run_book(rows=self.rows[:-1])
        self.assertEqual(self.calls,[])


if __name__ == "__main__":
    unittest.main()
