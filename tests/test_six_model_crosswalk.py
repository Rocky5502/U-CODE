"""M5: offline matrix crosswalk: no model downloads and no GPU spending."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.audit_six_model_crosswalk import validate_model_protocol_crosswalk

ROOT = Path(__file__).resolve().parents[1] / "configs"


class ModelCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = [
            json.loads((ROOT / name).read_text("utf-8")) for name in (
                "accepted_six_model_study_2026-10-25.json",
                "models_v2_2026-10-24.json",
                "ai_galaxy_six_model_deployment_2026-10-27.json",
                "confirmatory_sbse_protocol_2026-10-25.json",
            )
        ]

    def setUp(self):
        self.selected, self.inventory, self.deployment, self.protocol = deepcopy(
            self.original)

    def check(self):
        return validate_model_protocol_crosswalk(
            self.selected,self.inventory,self.deployment,self.protocol)

    def test_complete_six_roster_with_eight_policies_but_zero_experiments(self):
        x = self.check()
        self.assertEqual(len(x.models),6)
        self.assertEqual(x.policy_count,8)
        self.assertEqual(x.qualified_tasks,0)
        self.assertEqual(x.model_executions,0)
        self.assertEqual(x.paid_gpu_rentals,0)
        self.assertEqual(x.successful_benchmark_outcomes,0)
        self.assertTrue(all(not m.inference_approved and m.real_task_trials==0
                            for m in x.models))
        self.assertEqual(x.primary_treatment,"ucode_conditional_bes")
        self.assertEqual(x.primary_comparator,"no_uncertainty_search")

    def test_planned_unique_ports_and_a100_remain_reference_only(self):
        x=self.check()
        self.assertEqual([m.proposed_endpoint_port for m in x.models],list(range(8100,8106)))
        self.assertTrue(all("A100" in m.planned_gpu for m in x.models))

    def test_special_access_and_custom_code_risks_survive(self):
        x={m.model_id:m for m in self.check().models}
        self.assertEqual(
            x["deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"].additional_risk,
            "CUSTOM_MODEL_CODE_INDEPENDENT_SECURITY_AUDIT_REQUIRED")
        self.assertIn("MODEL_SPECIFIC_ACCESS_TERMS_REVIEW_REQUIRED",
                      x["google/codegemma-1.1-7b-it"].additional_risk)
        self.assertIn("MODEL_SPECIFIC_ACCESS_TERMS_REVIEW_REQUIRED",
                      x["meta-llama/Llama-3.1-8B-Instruct"].additional_risk)
        self.assertIn("A100_PRECISION_COMPATIBILITY_PREFLIGHT_REQUIRED",
                      x["mistralai/Devstral-Small-2-24B-Instruct-2512"].additional_risk)

    def test_per_model_blockers_cannot_be_silenced(self):
        x=self.check()
        self.assertTrue(all("checkpoint_revision_not_immutable" in r.study_blockers
                            for r in x.models))
        self.assertTrue(all(len(r.deployment_blockers)>0 for r in x.models))

    def test_crosswalk_refuses_tokenizer_revision_mismatch(self):
        self.deployment["models"][0]["tokenizer_revision"]="f"*40
        with self.assertRaisesRegex(ValueError,"revision"):
            self.check()

    def test_crosswalk_refuses_model_id_reordering(self):
        a=self.protocol["model_ids"]
        a[1],a[2]=a[2],a[1]
        with self.assertRaisesRegex(ValueError,"ordering"):
            self.check()

    def test_no_removed_mcts_or_replay_control(self):
        self.protocol["policy_ids"].remove("replay_search")
        with self.assertRaisesRegex(ValueError,"eight"):
            self.check()

    def test_deepseek_remote_code_risk_must_not_be_erased(self):
        self.deployment["models"][3]["untrusted_custom_model_code_must_be_reviewed"]=False
        with self.assertRaisesRegex(ValueError,"DeepSeek"):
            self.check()

    def test_restricted_terms_gate_must_not_be_erased(self):
        for i in (4,5):
            selected, inventory, dep, protocol = deepcopy(self.original)
            dep["models"][i]["restricted_terms_access_must_be_accepted"]=False
            with self.subTest(index=i),self.assertRaisesRegex(ValueError,"terms gate"):
                validate_model_protocol_crosswalk(selected,inventory,dep,protocol)

    def test_devstral_precision_gate_must_not_be_erased(self):
        self.deployment["models"][2]["model_native_fp8_engine_verification_required"]=False
        with self.assertRaisesRegex(ValueError,"Devstral"):
            self.check()

    def test_fake_model_inference_claim_rejected(self):
        self.selected["models"][0]["independently_verified_task_runs"]=1
        with self.assertRaisesRegex(ValueError,"nonzero"):
            self.check()

    def test_fake_task_admission_claim_rejected(self):
        self.protocol["qualified_task_ids"]=["PHP104"]
        with self.assertRaisesRegex(ValueError,"unqualified"):
            self.check()

    def test_fake_weight_approval_rejected(self):
        self.deployment["models"][0]["model_weights_verified"]=True
        with self.assertRaisesRegex(ValueError,"unverified"):
            self.check()


if __name__ == "__main__":
    unittest.main()
