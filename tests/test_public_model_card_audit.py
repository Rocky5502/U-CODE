"""Synthetic/adversarial integrity tests for public six-model observation audit.

No downloading weights, contacting private HF accounts or running inference.
"""
from __future__ import annotations

from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_six_public_model_cards import main
from ucode.public_model_card_audit import (
    ROOT, audit_public_card_observations, build_public_card_audit,
)


def inputs():
    paths = (
        "data/admission/2026-11-09/six_model_public_hub_cards_OBSERVATION_ONLY.json",
        "configs/accepted_six_model_study_2026-10-25.json",
        "configs/models_v2_2026-10-24.json",
        "configs/confirmatory_sbse_protocol_2026-10-25.json",
    )
    return tuple(json.loads((ROOT / n).read_text(encoding="utf-8"))
                 for n in paths)


class PublicModelCardAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot, cls.selected, cls.source, cls.protocol = inputs()

    def audit(self, snapshot=None, selected=None, source=None, protocol=None, **kwargs):
        return audit_public_card_observations(
            self.snapshot if snapshot is None else snapshot,
            self.selected if selected is None else selected,
            self.source if source is None else source,
            self.protocol if protocol is None else protocol,
            **kwargs)

    def test_six_models_never_self_qualify(self):
        r = self.audit()
        self.assertEqual(r["planned_models"], 6)
        self.assertEqual(r["actual_qualified_checkpoints"], 0)
        self.assertEqual(r["models_loaded_or_inferred"], 0)
        self.assertEqual(r["verified_private_model_accesses"], 0)
        self.assertEqual(r["real_model_outcomes"], 0)
        self.assertEqual(len(r["model_rows"]), 6)
        self.assertFalse(r["card_observations_authentic_signed_snapshots"])
        self.assertTrue(all(not m["model_runnable_for_study"] for m in r["model_rows"]))

    def test_deepseek_other_card_tag_disagrees_with_old_planning_label(self):
        r = self.audit()
        mismatched = [m for m in r["model_rows"] if
                      m["public_card_license_label_mismatch"]]
        self.assertEqual(r["public_license_label_mismatches"], 1)
        self.assertEqual(len(mismatched), 1)
        self.assertEqual(mismatched[0]["model_id"],
                         "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct")
        self.assertEqual(mismatched[0]["public_hub_license_tag_observed_not_legal_review"],
                         "other")
        self.assertEqual(mismatched[0]["historical_planning_license_label"],
                         "deepseek-license")

    def test_two_public_gated_tags_do_not_grant_private_access(self):
        r = self.audit()
        self.assertEqual(r["reported_public_card_gated_count"], 2)
        gated = [m["model_id"] for m in r["model_rows"]
                 if m["public_card_reports_gated_not_user_entitlement"]]
        self.assertEqual(gated, [
            "google/codegemma-1.1-7b-it",
            "meta-llama/Llama-3.1-8B-Instruct",
        ])
        self.assertTrue(all(not m["full_license_and_access_authorized"]
                            for m in r["model_rows"]))

    def test_rough_bf16_weight_storage_is_not_measured_feasibility(self):
        r = self.audit()
        rows = {x["model_id"]: x for x in r["model_rows"]}
        self.assertEqual(
            rows["Qwen/Qwen3-Coder-30B-A3B-Instruct"]["abstract_bf16_storage_class"],
            "ROUGH_WEIGHTS_ONLY_EXCEEDS_HYPOTHETICAL_CAPACITY")
        self.assertEqual(
            rows["Qwen/Qwen2.5-Coder-7B-Instruct"]["abstract_bf16_storage_class"],
            "ROUGH_WEIGHTS_ONLY_WITHIN_CAPACITY_NOT_LOAD_FEASIBILITY")
        self.assertTrue(all(not x["quantized_runtime_feasibility_proven"]
                            for x in r["model_rows"]))
        self.assertTrue(all(not x["actual_peak_vram_measured"]
                            for x in r["model_rows"]))
        self.assertTrue(r["bf16_estimates_are_rough_weights_only_not_runtime_predictions"])

    def test_hypothetical_capacity_cannot_be_pretended_hardware(self):
        low = self.audit(comparison_capacity_gib=8)
        high = self.audit(comparison_capacity_gib=80)
        self.assertEqual(low["hypothetical_hardware_gib_not_observed"], 8)
        self.assertEqual(high["hypothetical_hardware_gib_not_observed"], 80)
        self.assertTrue(any(x["abstract_bf16_storage_class"] ==
                            "ROUGH_WEIGHTS_ONLY_EXCEEDS_HYPOTHETICAL_CAPACITY"
                            for x in low["model_rows"]))
        self.assertFalse(any(x["abstract_bf16_storage_class"] ==
                             "ROUGH_WEIGHTS_ONLY_EXCEEDS_HYPOTHETICAL_CAPACITY"
                             for x in high["model_rows"]))
        self.assertEqual(high["actual_qualified_checkpoints"], 0)

    def test_bad_comparison_capacity_types_and_values_rejected(self):
        for value in (True, 0, -1, 1025, 16.0):
            with self.subTest(value=value), self.assertRaisesRegex(
                    ValueError, "hypothetical comparison capacity"):
                self.audit(comparison_capacity_gib=value)

    def test_snapshot_cannot_claim_rights_or_authentication(self):
        for key in (
            "all_model_checkpoint_revisions_independently_verified",
            "signed_card_snapshot_held",
            "authenticated_full_license_review_complete",
            "private_gated_access_validated", "runtime_vram_test_performed"):
            bad = deepcopy(self.snapshot)
            bad[key] = True
            with self.subTest(key=key), self.assertRaisesRegex(
                    ValueError, "cannot self-promote"):
                self.audit(snapshot=bad)

    def test_forged_model_sha_and_vram_rejected(self):
        for key, value in (("pin_model_sha40", "a"*40),
                           ("pin_tokenizer_sha40", "b"*40),
                           ("full_license_text_review_status", "APPROVED"),
                           ("account_terms_verified", True),
                           ("actual_weight_bytes_verified", True),
                           ("measured_peak_vram_gib", 14.5)):
            bad = deepcopy(self.snapshot)
            bad["observations"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(
                    ValueError, "does not authenticate"):
                self.audit(snapshot=bad)

    def test_duplicate_missing_or_reordered_model_rejected(self):
        for edit in ("duplicate", "remove", "reverse"):
            bad = deepcopy(self.snapshot)
            if edit == "duplicate":
                bad["observations"][1] = bad["observations"][0]
            elif edit == "remove":
                bad["observations"].pop()
            else:
                bad["observations"].reverse()
            with self.subTest(edit=edit), self.assertRaises(ValueError):
                self.audit(snapshot=bad)

    def test_unexpected_keys_and_edited_source_links_rejected(self):
        for kind in ("extra-top", "extra-row", "changed-url"):
            bad = deepcopy(self.snapshot)
            if kind == "extra-top":
                bad["model_weights_verified"] = True
            elif kind == "extra-row":
                bad["observations"][0]["hidden_approval"] = True
            else:
                bad["observations"][0]["card_url"] = "https://example.com"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.audit(snapshot=bad)

    def test_invalid_public_metadata_types_rejected(self):
        for key, value in (
            ("hub_license_id", "license:imaginary"),
            ("hub_card_reports_gated", "false"),
            ("reported_parameters_millions_approx", True),
            ("reported_parameters_millions_approx", float("nan")),
            ("reported_parameters_millions_approx", -1),
            ("architecture_tag", "hidden_unknown"),
            ("library_tag", "unapproved_engine"),
        ):
            bad = deepcopy(self.snapshot)
            bad["observations"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.audit(snapshot=bad)

    def test_frozen_study_identity_drift_rejected(self):
        p = deepcopy(self.protocol)
        p["model_ids"][0] = "other/model"
        with self.assertRaisesRegex(ValueError, "frozen model roster"):
            self.audit(protocol=p)

    def test_future_results_cannot_be_fabricated_by_card_snapshot(self):
        bad = deepcopy(self.snapshot)
        bad["real_model_inferences"] = 1
        with self.assertRaisesRegex(ValueError, "cannot self-promote"):
            self.audit(snapshot=bad)
        p = deepcopy(self.protocol)
        p["results_measured"] = True
        with self.assertRaisesRegex(ValueError, "false readiness claims"):
            self.audit(protocol=p)

    def test_cli_public_output_and_strict_blocked_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "hub_public.json"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--output", str(out)]), 0)
                self.assertEqual(main(["--require-six-ready"]), 2)
            obj = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(obj, build_public_card_audit())
            self.assertNotIn("access_token", out.read_text("utf-8"))
            self.assertEqual(obj["actual_qualified_checkpoints"], 0)

    def test_public_cli_refuses_symlink_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "do_not_overwrite.json"
            original.write_text("protected", encoding="utf-8")
            alias = Path(tmp) / "symlink.json"
            alias.symlink_to(original)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(
                    ValueError, "symlink"):
                main(["--output", str(alias)])
            self.assertEqual(original.read_text(encoding="utf-8"), "protected")


if __name__ == "__main__":
    unittest.main()
