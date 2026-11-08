"""Regression tests: self-reported planning metadata cannot approve model runtime.

All hashes/approval fields in these tests are INVENTED local fixtures.
No real model weights, licensed terms, external reviewer signatures, GPUs,
Hub requests, inference or third-party code are used.
"""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from ucode.model_readiness import (
    EXTERNAL_EVIDENCE_BLOCKER,
    ModelReadiness,
    SOURCE_V2,
    load_selected_models,
    require_full_six_model_readiness,
    validate_selected_manifest,
)
from ucode.real_trial_phase0 import build_real_trial_phase0
import ucode.real_trial_phase0 as phase


def fixture():
    return (
        load_selected_models(),
        json.loads(SOURCE_V2.read_text(encoding="utf-8")),
    )


def self_approve(model):
    # Synthetic "looks ready" values, not a claim any real model was loaded.
    model.update({
        "full_license_review": "APPROVED",
        "gated_terms_verified": True,
        "checkpoint_revision": "a" * 40,
        "tokenizer_revision": "b" * 40,
        "frozen_chat_template_sha256": "c" * 64,
        "engine_version": "fictional-1.2.3",
        "quantization_format": "fictional-bf16",
        "measured_peak_vram_gb": 10.5,
        "model_weights_verified": True,
        "passed_sandbox_security_review": True,
    })


class ModelSelfAttestationBoundaryTests(unittest.TestCase):
    def test_all_six_have_external_evidence_blocker(self):
        selected, originals = fixture()
        result = validate_selected_manifest(selected, originals)
        self.assertEqual(len(result), 6)
        for item in result:
            self.assertIn(EXTERNAL_EVIDENCE_BLOCKER, item.blockers)
            self.assertTrue(item.accepted_for_planning)
            self.assertFalse(item.runnable)

    def test_each_individual_synthetic_perfect_model_still_blocked(self):
        selected, originals = fixture()
        for i in range(6):
            changed = deepcopy(selected)
            self_approve(changed["models"][i])
            result = validate_selected_manifest(changed, originals)
            with self.subTest(i=i):
                self.assertFalse(result[i].runnable)
                self.assertIn(EXTERNAL_EVIDENCE_BLOCKER, result[i].blockers)
                self.assertIn(
                    "self_reported_approval_not_authenticated", result[i].blockers)

    def test_six_forged_perfect_models_cannot_unlock_full_study(self):
        selected, originals = fixture()
        for model in selected["models"]:
            self_approve(model)
        result = validate_selected_manifest(selected, originals)
        self.assertFalse(any(x.runnable for x in result))
        with self.assertRaisesRegex(ValueError, "six-model experiment BLOCKED"):
            require_full_six_model_readiness(result)

    def test_forged_direct_dataclass_cannot_become_execution_certificate(self):
        selected, _ = fixture()
        forged = tuple(
            ModelReadiness(model["model_id"], True, ())
            for model in selected["models"]
        )
        self.assertFalse(any(r.runnable for r in forged))
        with self.assertRaisesRegex(ValueError, "six-model experiment BLOCKED"):
            require_full_six_model_readiness(forged)

    def test_historical_planning_manifest_cannot_claim_completed_model_run(self):
        selected, original = fixture()
        selected["models"][0]["inference_execution_status"] = "COMPLETED_AND_AUDITED"
        with self.assertRaisesRegex(ValueError, "cannot self-certify"):
            validate_selected_manifest(selected, original)

    def test_disallow_nonzero_forged_runs_even_with_not_run_status(self):
        selected, original = fixture()
        for fake in (1, True, 500, -1, "0"):
            modified = deepcopy(selected)
            modified["models"][0]["independently_verified_task_runs"] = fake
            with self.subTest(fake=fake), self.assertRaisesRegex(
                    ValueError, "nonzero experiment count"):
                validate_selected_manifest(modified, original)

    def test_malformed_manifest_non_objects_refused(self):
        selected, original = fixture()
        for p, s in ((None, original), (selected, []),
                     ("manipulated", original), (selected, "invalid")):
            with self.subTest(p=type(p), s=type(s)), self.assertRaises(TypeError):
                validate_selected_manifest(p, s)

    def test_fake_self_authorized_list_not_accepted_as_runner_ready(self):
        selected, original = fixture()
        genuine = validate_selected_manifest(selected, original)
        fake = tuple(ModelReadiness(x.model_id, True, ())
                     for x in genuine)
        with patch.object(phase, "validate_selected_manifest", return_value=fake):
            with self.assertRaisesRegex(ValueError, "blocker inconsistency"):
                build_real_trial_phase0()

    def test_forged_external_blocker_drift_detected_by_phase0(self):
        selected, original = fixture()
        genuine = list(validate_selected_manifest(selected, original))
        genuine[2] = ModelReadiness(
            genuine[2].model_id,
            True,
            ("checkpoint_revision_not_immutable",),
        )
        with patch.object(phase, "validate_selected_manifest",
                          return_value=tuple(genuine)):
            with self.assertRaisesRegex(ValueError, "blocker inconsistency"):
                build_real_trial_phase0()

    def test_made_up_structural_prerequisites_still_cannot_grant_six_approval(self):
        selected, original = fixture()
        result = validate_selected_manifest(selected, original)
        for fabricated in (
            tuple(ModelReadiness(x.model_id, True, ("fake",)) for x in result),
            tuple(ModelReadiness(x.model_id, True, ()) for x in result),
        ):
            with self.assertRaisesRegex(ValueError, "six-model experiment BLOCKED"):
                require_full_six_model_readiness(fabricated)

    def test_study_roster_mismatch_does_not_allow_proxy_model(self):
        selected, original = fixture()
        selected["models"][0]["model_id"] = "Unrelated/Model"
        with self.assertRaises(ValueError):
            validate_selected_manifest(selected, original)


if __name__ == "__main__":
    unittest.main()
