"""All eight registered policy slots through one *synthetic-only* blind runner."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import unittest

from ucode.blind_policy_trace import BlindAction, PublicToolReceipt
from ucode.experiment_contract import FrozenStudy
from ucode.shadow_assignment_parity import AssignedOpportunity
from ucode.shadow_eight_arm_runner import run_shadow_eight_arm_matrix
from ucode.task_view_boundary import parse_agent_task_view
from ucode.vector_policy import ResourceVector as RV

ROOT = Path(__file__).resolve().parents[1]


class ShadowEightArmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = json.loads((ROOT / "configs/confirmatory_sbse_protocol_2026-10-25.json").read_text("utf-8"))
        cls.model_ids = tuple(spec["model_ids"])
        cls.policy_ids = tuple(spec["policy_ids"])

    def setUp(self):
        task_text = "SYNTHETIC ONLY: no external code, no oracle."
        self.task = parse_agent_task_view({
            "repository": "synthetic/fixture",
            "base_sha": "a"*40,
            "prefixed_spec": task_text,
            "spec_sha256": sha256(task_text.encode()).hexdigest(),
        })
        self.cap = RV(tokens=30, test_calls=2, gpu_seconds=1, cpu_seconds=2, wall_seconds=3)
        self.study = FrozenStudy(
            (("SYNTHETIC_OFFLINE_TASK", "SYNTHETIC_LINEAGE"),),
            self.model_ids, self.policy_ids, (11,),
            (("SYNTHETIC_ONLY_CAP",self.cap),))
        self.assignments = tuple(AssignedOpportunity(
            task_id="SYNTHETIC_OFFLINE_TASK",
            lineage_group="SYNTHETIC_LINEAGE",
            model_id=model,policy_id=policy,seed=11,
            budget_id="SYNTHETIC_ONLY_CAP",
            pre_fix_base_sha40=self.task.base_sha,
            model_checkpoint_sha40="b"*40,
            task_spec_sha256=self.task.spec_sha256,
            public_candidate_archive_sha256="d"*64,
            common_opportunity_catalog_sha256="e"*64,
            tool_access_sha256="f"*64,
            environment_image_sha256="1"*64,
            resource_cap=self.cap,
        ) for model in self.model_ids for policy in self.policy_ids)
        self.calls=[]
        def scripted_factory(assignment):
            self.calls.append(("make_handler",assignment.model_id,assignment.policy_id))
            def scripted(state):
                if not state.history:
                    return BlindAction("generate",RV(tokens=10,cpu_seconds=1,wall_seconds=1))
                if len(state.history)==1:
                    return BlindAction("test",RV(test_calls=1,wall_seconds=1))
                return BlindAction("release",RV())
            return scripted
        self.handlers={p:scripted_factory for p in self.policy_ids}
        def public_factory(assignment):
            self.calls.append(("make_public_tool",assignment.model_id,assignment.policy_id))
            def tool(action,view,prior,history):
                if action.kind=="generate":
                    return PublicToolReceipt("generate",RV(tokens=8,cpu_seconds=1,wall_seconds=1),
                                             patch="SYNTHETIC patch only")
                if action.kind=="test":
                    return PublicToolReceipt("test",RV(test_calls=1,wall_seconds=1),
                                             feedback="PUBLIC SYNTHETIC diagnostic")
                raise AssertionError("not an offline reference action")
            return tool
        self.tools=public_factory
        self.views={"SYNTHETIC_OFFLINE_TASK":self.task}

    def check(self,assignments=None, handlers=None, task_views=None, tools=None, study=None):
        return run_shadow_eight_arm_matrix(
            self.study if study is None else study,
            self.assignments if assignments is None else assignments,
            self.views if task_views is None else task_views,
            self.handlers if handlers is None else handlers,
            self.tools if tools is None else tools)

    def test_all_eight_arms_all_six_names_share_blind_tool_contract(self):
        x=self.check()
        self.assertEqual(x.total_shadow_arm_wirings,48)
        self.assertEqual({a.policy_id for a in x.arms},set(self.policy_ids))
        self.assertEqual({a.model_id for a in x.arms},set(self.model_ids))
        self.assertEqual({a.terminal_status for a in x.arms},
                         {"RELEASED_PENDING_INDEPENDENT_EVALUATION"})
        self.assertEqual({a.public_action_count for a in x.arms},{2})
        self.assertEqual({a.reported_remaining.tokens for a in x.arms},{22})
        self.assertEqual({a.reported_remaining.test_calls for a in x.arms},{1})
        self.assertEqual(x.real_task_successes,0)
        self.assertEqual(x.authorized_external_executions,0)
        self.assertEqual(x.independent_oracle_labels,0)
        self.assertEqual(x.verified_model_inferences,0)
        self.assertFalse(x.policy_fidelity_attested)
        self.assertFalse(x.verified_hardware_metering)
        self.assertEqual(len(self.calls),96)

    def test_deterministic_replay_and_no_raw_patch_in_output(self):
        x=self.check()
        digest=x.arms[0].visible_trace_sha256
        self.assertEqual(x.declared_assignment_sha256,
                         self.check(tuple(reversed(self.assignments))).declared_assignment_sha256)
        self.assertEqual(digest,self.check().arms[0].visible_trace_sha256)
        self.assertNotIn("SYNTHETIC patch only",str(x))

    def test_five_budget_mismatch_rejected_before_any_callback(self):
        rows=list(self.assignments)
        rows[0]=replace(rows[0],resource_cap=RV(tokens=31,test_calls=2,
                            gpu_seconds=1,cpu_seconds=2,wall_seconds=3))
        with self.assertRaisesRegex(ValueError,"budget"):
            self.check(tuple(rows))
        self.assertEqual(self.calls,[])

    def test_mismatched_task_spec_rejected_before_any_callback(self):
        rows=list(self.assignments)
        rows=[replace(x,task_spec_sha256="c"*64) for x in rows]
        with self.assertRaisesRegex(ValueError,"task/spec"):
            self.check(tuple(rows))
        self.assertEqual(self.calls,[])

    def test_missing_policy_arm_rejected_before_any_callback(self):
        with self.assertRaisesRegex(ValueError,"incomplete"):
            self.check(self.assignments[:-1])
        self.assertEqual(self.calls,[])

    def test_missing_policy_factory_rejected_before_any_callback(self):
        h=dict(self.handlers)
        del h[self.policy_ids[0]]
        with self.assertRaisesRegex(ValueError,"eight policy handler"):
            self.check(handlers=h)
        self.assertEqual(self.calls,[])

    def test_additional_oracle_approval_in_registration_forbidden(self):
        bad=dict(self.views)
        bad["hidden_oracle"]="SECRET"
        with self.assertRaisesRegex(ValueError,"missing/extra"):
            self.check(task_views=bad)
        self.assertEqual(self.calls,[])
        with self.assertRaises(TypeError):
            self.check(oracle_verdicts=[])

    def test_incorrect_pre_fix_base_rejected_before_callback(self):
        rows=[replace(x,pre_fix_base_sha40="0"*40) for x in self.assignments]
        with self.assertRaisesRegex(ValueError,"task/spec"):
            self.check(tuple(rows))
        self.assertEqual(self.calls,[])

    def test_adapter_cost_overrun_fails_closed_without_released_patch(self):
        def factory(row):
            def tool(*args):
                return PublicToolReceipt("generate",RV(tokens=11),patch="SYNTHETIC")
            return tool
        x=self.check(tools=factory)
        self.assertEqual({a.terminal_status for a in x.arms},{"TOOL_COST_OVERRUN"})
        self.assertTrue(all(a.patch_sha256 is None and
                            not a.accounting_verified_by_schema_only
                            for a in x.arms))

    def test_missing_public_tool_fails_closed_without_hidden_error_string(self):
        def factory(row):
            def tool(*args):
                raise RuntimeError("secret private oracle should never appear")
            return tool
        x=self.check(tools=factory)
        self.assertEqual({a.terminal_status for a in x.arms},
                         {"TOOL_FAILED_COST_UNVERIFIED"})
        self.assertNotIn("private oracle",str(x))

    def test_abstentions_remain_in_full_denominator_not_successes(self):
        def factory(row):
            return lambda s: BlindAction("abstain",RV())
        x=self.check(handlers={p:factory for p in self.policy_ids})
        self.assertEqual(x.total_shadow_arm_wirings,48)
        self.assertTrue(all(a.terminal_status=="ABSTAINED" and
                            a.patch_sha256 is None and a.public_action_count==0
                            for a in x.arms))
        self.assertEqual(x.real_task_successes,0)

    def test_untrusted_policy_factory_result_rejected(self):
        def factory(row):
            return None
        with self.assertRaisesRegex(TypeError,"callable"):
            self.check(handlers={p:factory for p in self.policy_ids})

    def test_registry_must_retain_all_six_models(self):
        reduced=FrozenStudy(self.study.task_lineages,self.model_ids[:-1],
                            self.policy_ids,self.study.seeds,self.study.budgets)
        with self.assertRaisesRegex(ValueError,"six planned models"):
            self.check(study=reduced)

    def test_status_not_falsely_promoted_to_real_evaluation(self):
        x=self.check()
        self.assertIn("NOT_EIGHT_FAITHFUL_ALGORITHMS",x.stage)
        self.assertFalse(any(hasattr(a,"oracle_passed") for a in x.arms))


if __name__ == "__main__":
    unittest.main()
