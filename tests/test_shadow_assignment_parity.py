"""Offline M4 treatment/control opportunity fairness audit; no model calls."""
from dataclasses import replace
import json
from pathlib import Path
import unittest

from ucode.experiment_contract import FrozenStudy
from ucode.shadow_assignment_parity import (
    AssignedOpportunity, audit_shadow_assignment_parity,
)
from ucode.vector_policy import ResourceVector as RV

ROOT = Path(__file__).resolve().parents[1]


class ShadowParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        protocol = json.loads((ROOT / "configs/confirmatory_sbse_protocol_2026-10-25.json").read_text("utf-8"))
        cls.models = tuple(protocol["model_ids"])
        cls.policies = tuple(protocol["policy_ids"])

    def setUp(self):
        cap = RV(tokens=100, test_calls=3, gpu_seconds=9,
                 cpu_seconds=12, wall_seconds=20)
        self.study = FrozenStudy(
            (("SYNTHETIC_ONLY_A", "lineage-A"),), self.models,
            self.policies, (11, 29), (("dry_shadow_B", cap),))
        self.rows = tuple(AssignedOpportunity(
            task_id=task,lineage_group="lineage-A",model_id=model,
            policy_id=policy,seed=seed,budget_id=budget,
            pre_fix_base_sha40="a"*40,
            model_checkpoint_sha40="b"*40,
            task_spec_sha256="c"*64,
            public_candidate_archive_sha256="d"*64,
            common_opportunity_catalog_sha256="e"*64,
            tool_access_sha256="f"*64,
            environment_image_sha256="1"*64,
            resource_cap=cap,
        ) for task,model,seed,budget,policy in (
            (t,m,s,z,p) for t,_ in self.study.task_lineages
            for m in self.models for s in self.study.seeds
            for z,_ in self.study.budgets for p in self.policies))

    def check(self, rows=None, study=None):
        return audit_shadow_assignment_parity(
            self.study if study is None else study,
            self.rows if rows is None else rows,
        )

    def test_eight_policy_six_model_two_seed_shadow_is_valid(self):
        result = self.check()
        self.assertEqual(result.verified_shadow_assignments, 96)
        self.assertEqual(result.matrix_pairs, 12)
        self.assertEqual(result.policies_per_pair, 8)
        self.assertEqual(result.approved_real_tasks, 0)
        self.assertEqual(result.independent_oracle_results, 0)
        self.assertFalse(result.authenticated_shared_draws)
        self.assertEqual(len(result.declared_assignment_digest), 64)

    def test_order_independent_deterministic_digest(self):
        self.assertEqual(self.check().declared_assignment_digest,
                         self.check(tuple(reversed(self.rows))).declared_assignment_digest)

    def test_missing_treatment_arm_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.check(self.rows[1:])

    def test_duplicate_comparator_cannot_displace_other_arm(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check((self.rows[0],)+self.rows[:-1])

    def test_rogue_policy_cannot_replace_registered_policy(self):
        rows = list(self.rows)
        rows[0] = replace(rows[0],policy_id="extra_control")
        with self.assertRaisesRegex(ValueError, "unregistered"):
            self.check(tuple(rows))

    def test_each_five_dimensional_budget_is_equal(self):
        cap = self.rows[0].resource_cap
        for name,val in (("tokens",101),("test_calls",4),
                         ("gpu_seconds",10),("cpu_seconds",13),("wall_seconds",21)):
            rows = list(self.rows)
            costs = {f:getattr(cap,f) for f in (
                "tokens","test_calls","gpu_seconds","cpu_seconds","wall_seconds")}
            costs[name] = val
            rows[0] = replace(rows[0], resource_cap=RV(**costs))
            with self.subTest(resource=name),self.assertRaisesRegex(ValueError,"five-budget"):
                self.check(tuple(rows))

    def test_shared_archive_and_actions_must_match_all_arms(self):
        for field in ("public_candidate_archive_sha256",
                      "common_opportunity_catalog_sha256"):
            rows=list(self.rows)
            rows[0]=replace(rows[0],**{field:"0"*64})
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,"unequal public opportunities"):
                self.check(tuple(rows))

    def test_visible_task_context_must_match_across_policies(self):
        rows=list(self.rows)
        rows[0]=replace(rows[0],task_spec_sha256="2"*64)
        with self.assertRaisesRegex(ValueError,"visible task spec"):
            self.check(tuple(rows))

    def test_original_pre_fix_base_cannot_differ(self):
        rows=list(self.rows)
        rows[0]=replace(rows[0],pre_fix_base_sha40="3"*40)
        with self.assertRaisesRegex(ValueError,"pre-fix source base"):
            self.check(tuple(rows))

    def test_model_checkpoint_is_stable_across_seeds_and_policies(self):
        rows=list(self.rows)
        rows[0]=replace(rows[0],model_checkpoint_sha40="4"*40)
        with self.assertRaisesRegex(ValueError,"model checkpoint"):
            self.check(tuple(rows))

    def test_environment_and_tool_access_cannot_drift(self):
        for field, msg in (
            ("environment_image_sha256","environment"),
            ("tool_access_sha256","tool availability"),
        ):
            rows=list(self.rows)
            rows[0]=replace(rows[0],**{field:"8"*64})
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,msg):
                self.check(tuple(rows))

    def test_no_gold_oracle_feedback_in_planning_object(self):
        with self.assertRaises(TypeError):
            replace(self.rows[0],oracle_passed=True)
        with self.assertRaises(TypeError):
            AssignedOpportunity(**{**self.rows[0].__dict__,"hidden_test":"solution"})
        with self.assertRaisesRegex(ValueError,"does not certify real"):
            replace(self.rows[0],stage="EXECUTED_VALIDATED")

    def test_no_ambiguous_commit_or_float_seed(self):
        with self.assertRaisesRegex(ValueError,"SHA40"):
            replace(self.rows[0],model_checkpoint_sha40="main")
        with self.assertRaisesRegex(ValueError,"seed"):
            replace(self.rows[0],seed=11.0)
        with self.assertRaisesRegex(ValueError,"seed"):
            replace(self.rows[0],seed=True)

    def test_wrong_lineage_and_model_pair_rejected(self):
        rows=list(self.rows)
        rows[0]=replace(rows[0],lineage_group="wrong-fork")
        with self.assertRaisesRegex(ValueError,"lineage"):
            self.check(tuple(rows))

    def test_untyped_list_rejected(self):
        with self.assertRaisesRegex(ValueError,"immutable"):
            self.check(list(self.rows))


if __name__ == "__main__":
    unittest.main()
