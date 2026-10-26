"""Synthetic-only validation of six-model rental GPU staging, no model downloads."""
from copy import deepcopy
import unittest

from scripts.plan_ai_galaxy_six_models import inspect_plan, load_plan

SELECTED, PLAN = load_plan()


class AIGalaxyModelPlanningTests(unittest.TestCase):
    def test_exact_six_selected_models_are_present(self):
        entries = inspect_plan(SELECTED, PLAN)
        self.assertEqual(len(entries), 6)
        self.assertEqual([e.model_id for e in entries],
                         [m["model_id"] for m in SELECTED["models"]])

    def test_no_model_claims_executable_or_inference(self):
        entries = inspect_plan(SELECTED, PLAN)
        self.assertTrue(all(not e.executable and len(e.blockers) >= 6
                            for e in entries))
        self.assertTrue(all(m["model_inference_executed"] is False
                            for m in PLAN["models"]))

    def test_model_ids_cannot_be_replaced(self):
        plan = deepcopy(PLAN)
        plan["models"][3]["model_id"] = "other/random-checkpoint"
        with self.assertRaisesRegex(ValueError, "match"):
            inspect_plan(SELECTED, plan)

    def test_model_order_cannot_be_silently_shuffled(self):
        plan = deepcopy(PLAN)
        plan["models"][0], plan["models"][1] = (
            plan["models"][1], plan["models"][0])
        with self.assertRaisesRegex(ValueError, "match"):
            inspect_plan(SELECTED, plan)

    def test_duplicate_endpoint_port_rejected(self):
        plan = deepcopy(PLAN)
        plan["models"][2]["vllm_openai_compatible_endpoint_port"] = 8101
        with self.assertRaisesRegex(ValueError, "unique"):
            inspect_plan(SELECTED, plan)

    def test_unverified_revisions_must_be_null_or_40hex(self):
        plan = deepcopy(PLAN)
        plan["models"][0]["checkpoint_revision"] = "main"
        with self.assertRaisesRegex(ValueError, "40-hex"):
            inspect_plan(SELECTED, plan)

    def test_different_canonical_revision_rejected(self):
        plan = deepcopy(PLAN)
        plan["models"][0]["checkpoint_revision"] = "a"*40
        with self.assertRaisesRegex(ValueError, "mismatches"):
            inspect_plan(SELECTED, plan)

    def test_unreviewed_weights_cannot_be_claimed_verified(self):
        plan = deepcopy(PLAN)
        plan["models"][0]["model_weights_verified"] = True
        with self.assertRaisesRegex(ValueError, "unverified"):
            inspect_plan(SELECTED, plan)

    def test_unreviewed_license_cannot_be_claimed_approved(self):
        plan = deepcopy(PLAN)
        plan["models"][0]["license_and_terms_approved"] = True
        with self.assertRaisesRegex(ValueError, "silently approved"):
            inspect_plan(SELECTED, plan)

    def test_misleading_execution_status_rejected(self):
        plan = deepcopy(PLAN)
        plan["models"][0]["model_inference_executed"] = True
        with self.assertRaisesRegex(ValueError, "execution"):
            inspect_plan(SELECTED, plan)

    def test_preflight_requires_all_nine_gates(self):
        plan = deepcopy(PLAN)
        del plan["deployment_gates"]["independent_resource_monitoring"]
        with self.assertRaisesRegex(ValueError, "nine"):
            inspect_plan(SELECTED, plan)
        plan = deepcopy(PLAN)
        plan["deployment_gates"]["independent_resource_monitoring"] = False
        with self.assertRaisesRegex(ValueError, "disable"):
            inspect_plan(SELECTED, plan)

    def test_profile_cannot_claim_zero_or_fewer_gpus(self):
        plan = deepcopy(PLAN)
        plan["profiles"]["simultaneous_six_gpu"]["requested_gpu_count"] = 4
        with self.assertRaisesRegex(ValueError, "contradictory"):
            inspect_plan(SELECTED, plan)

    def test_unmeasured_large_context_rejected(self):
        plan = deepcopy(PLAN)
        plan["models"][1]["max_model_len_tokens_initial"] = 262144
        with self.assertRaisesRegex(ValueError, "context"):
            inspect_plan(SELECTED, plan)

    def test_preflight_rejects_unsafe_gpu_memory_utilization(self):
        plan = deepcopy(PLAN)
        plan["models"][0]["memory_utilization_ceiling"] = 1.0
        with self.assertRaisesRegex(ValueError, "memory"):
            inspect_plan(SELECTED, plan)

    def test_parallel_sequences_not_falsely_benchmarked(self):
        plan = deepcopy(PLAN)
        plan["models"][0]["max_num_seqs_initial"] = 16
        with self.assertRaisesRegex(ValueError, "concurrent"):
            inspect_plan(SELECTED, plan)

    def test_custom_remote_code_not_auto_authorized(self):
        rows = inspect_plan(SELECTED, PLAN)
        x = next(r for r in rows if r.model_id.startswith("deepseek-ai/"))
        self.assertIn("untrusted_custom_code_security_review_missing",
                      x.blockers)

    def test_gated_accounts_not_auto_authorized(self):
        rows = inspect_plan(SELECTED, PLAN)
        for prefix in ("google/", "meta-llama/"):
            x = next(r for r in rows if r.model_id.startswith(prefix))
            self.assertIn("gated_provider_terms_not_accepted", x.blockers)

    def test_fp8_accelerator_compatibility_not_assumed(self):
        rows = inspect_plan(SELECTED, PLAN)
        x = next(r for r in rows if r.model_id.startswith("mistralai/"))
        self.assertEqual(x.gpu, "A100-SXM4-80GB")
        self.assertIn("native_fp8_accelerator_compatibility_not_tested",
                      x.blockers)

    def test_single_A100_GPU_type_for_all_six(self):
        models = inspect_plan(SELECTED, PLAN)
        self.assertEqual({m.gpu for m in models}, {"A100-SXM4-80GB"})
        self.assertEqual(PLAN["profiles"]["sequential_one_gpu"]["requested_gpu_count"], 1)

    def test_h100_requirement_cannot_be_reintroduced(self):
        plan = deepcopy(PLAN)
        plan["models"][2]["rental_gpu_for_initial_preflight"] = "H100-80GB"
        with self.assertRaisesRegex(ValueError, "ONE A100"):
            inspect_plan(SELECTED, plan)

    def test_devstral_fallback_is_explicitly_unverified(self):
        plan = deepcopy(PLAN)
        plan["models"][2]["ampere_fp8_fallback_kernel"] = "NATIVE_A100_W8A8"
        with self.assertRaisesRegex(ValueError, "Marlin fallback"):
            inspect_plan(SELECTED, plan)

    def test_sequential_profile_cannot_switch_to_another_gpu_family(self):
        plan = deepcopy(PLAN)
        plan["profiles"]["sequential_one_gpu"]["required_gpu_model"] = "H100"
        with self.assertRaisesRegex(ValueError, "A100 hardware"):
            inspect_plan(SELECTED, plan)

    def test_proposed_bf16_weight_floor_excludes_kv_cache(self):
        rows = inspect_plan(SELECTED, PLAN)
        self.assertGreater(max(x.weight_floor_gb for x in rows), 60)
        self.assertTrue(all(m["bf16_weights_are_not_total_vram"] is True
                            for m in PLAN["models"]))


if __name__ == "__main__":
    unittest.main()
