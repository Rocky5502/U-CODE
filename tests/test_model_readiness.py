"""No model weights are downloaded: six user-selected model planning checks."""
from copy import deepcopy
import unittest

from ucode.model_readiness import (
    SOURCE_V2, load_selected_models, preflight_selected_models,
    require_full_six_model_readiness, validate_selected_manifest,
)
import json


class SixModelPreflightTests(unittest.TestCase):
    def setUp(self):
        self.plan = load_selected_models()
        self.v2 = json.loads(SOURCE_V2.read_text(encoding="utf-8"))

    def check(self):
        return validate_selected_manifest(self.plan, self.v2)

    def test_all_six_selected_for_planning(self):
        r = self.check()
        self.assertEqual(len(r), 6)
        self.assertTrue(all(x.accepted_for_planning for x in r))
        self.assertEqual(len({x.model_id for x in r}), 6)

    def test_no_false_claim_models_ready_or_executed(self):
        r = preflight_selected_models()
        self.assertTrue(all(not x.runnable for x in r))
        with self.assertRaisesRegex(ValueError, "experiment BLOCKED"):
            require_full_six_model_readiness(r)

    def test_no_hallucinated_checkpoint_revision(self):
        for r in self.check():
            self.assertIn("checkpoint_revision_not_immutable", r.blockers)
            self.assertIn("tokenizer_revision_not_immutable", r.blockers)

    def test_user_approval_does_not_mark_license_accepted(self):
        for r in self.check():
            self.assertIn("license_text_not_approved", r.blockers)
        by_name = {r.model_id:r for r in self.check()}
        self.assertIn("gated_terms_unverified",
                      by_name["google/codegemma-1.1-7b-it"].blockers)
        self.assertIn("gated_terms_unverified",
                      by_name["meta-llama/Llama-3.1-8B-Instruct"].blockers)

    def test_cannot_silently_drop_the_large_models(self):
        self.plan["models"].pop(1)
        with self.assertRaisesRegex(ValueError, "six"):
            self.check()

    def test_duplicate_qwen_cannot_displace_another_family(self):
        self.plan["models"][1]["model_id"] = self.plan["models"][0]["model_id"]
        with self.assertRaisesRegex(ValueError, "exactly match"):
            self.check()

    def test_drifted_model_card_url_blocked(self):
        self.plan["models"][0]["card_url"] = "https://example.org/model"
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.check()

    def test_fake_successful_runs_before_inference_blocked(self):
        self.plan["models"][2]["independently_verified_task_runs"] = 200
        with self.assertRaisesRegex(ValueError, "nonzero"):
            self.check()

    def test_invalid_status_blocked(self):
        self.plan["models"][1]["inference_execution_status"] = "COMPLETED"
        with self.assertRaisesRegex(ValueError, "unknown"):
            self.check()

    def test_bogus_revision_strings_do_not_unblock_model(self):
        x = self.plan["models"][0]
        x["checkpoint_revision"] = "main"
        x["tokenizer_revision"] = "latest"
        reasons = self.check()[0].blockers
        self.assertIn("checkpoint_revision_not_immutable", reasons)
        self.assertIn("tokenizer_revision_not_immutable", reasons)

    def test_missing_model_memory_measurement_blocks_execution(self):
        self.assertTrue(all(
            "gpu_peak_unmeasured" in x.blockers
            for x in self.check()
        ))

    def test_one_model_can_become_ready_only_with_complete_audited_gates(self):
        x = self.plan["models"][0]
        x.update(
            full_license_review="APPROVED",
            checkpoint_revision="a"*40,
            tokenizer_revision="b"*40,
            frozen_chat_template_sha256="c"*64,
            engine_version="pinned-mocked-version-for-fixture",
            quantization_format="mock-fp16",
            measured_peak_vram_gb=9.5,
            model_weights_verified=True,
            passed_sandbox_security_review=True,
        )
        reports = self.check()
        self.assertTrue(reports[0].runnable)
        self.assertFalse(reports[1].runnable)
        with self.assertRaisesRegex(ValueError, "six-model experiment BLOCKED"):
            require_full_six_model_readiness(reports)

    def test_diagnostic_cannot_claim_six_without_six_objects(self):
        with self.assertRaisesRegex(ValueError, "six-model experiment"):
            require_full_six_model_readiness(())


if __name__ == "__main__":
    unittest.main()
