"""Adversarial S05–S10 source-ledger crosschecks, no real execution."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import json
import unittest

from ucode.critical_path import ROOT, build_critical_path
from ucode.pilot_preflight import build_pilot_preflight
from ucode.public_model_card_audit import build_public_card_audit
from ucode.remaining_stage_evidence import (
    STAGE, METHOD_GAPS, SCOPE, audit_remaining_stage_evidence,
    build_remaining_stage_evidence,
)


def local(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))


class RemainingStageEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.originals = (
            local("configs/confirmatory_sbse_protocol_2026-10-25.json"),
            build_pilot_preflight(ROOT),
            build_critical_path(ROOT),
            build_public_card_audit(root=ROOT),
            local("data/admission/2026-11-07/"
                  "go43_pre_fix_oracle_review_blueprint_PUBLIC_NO_GOLD.json"),
            local("data/admission/2026-10-28/"
                  "php104_oracle_review_blueprint_PUBLIC_NO_GOLD.json"),
            (ROOT/"paper/overleaf/main.tex").read_text(encoding="utf-8"),
        )

    def report(self, at=None, transform=None):
        values = list(deepcopy(self.originals))
        if at is not None:
            if transform is None:
                raise AssertionError("test transform required")
            transform(values[at])
        return audit_remaining_stage_evidence(*values)

    def test_real_first_party_sources_still_block_six_registered_stages(self):
        x = build_remaining_stage_evidence()
        self.assertEqual(x["stage"], STAGE)
        self.assertEqual(tuple(x["sprint_stage_ids"]), SCOPE)
        self.assertEqual(tuple(x["sprint_issue_numbers"]),
                         (65,66,67,68,69,70))
        self.assertEqual(x["external_task_admission_gates_pending"], 16)
        self.assertEqual(x["independently_admitted_tasks"], 0)
        self.assertEqual(x["model_slots_not_qualified"], 6)
        self.assertEqual(x["scientific_exit_criteria_pending"], 10)
        self.assertIsNone(x["measured_primary_effect"])
        self.assertTrue(x["no_execution_permit"])
        self.assertFalse(x["overleaf_live_sync_verified"])

    def test_eight_methods_must_not_be_read_as_eight_faithful_algorithms(self):
        x = self.report()
        self.assertEqual(len(x["policy_fidelity_review"]), 8)
        self.assertEqual({r["policy_id"] for r in
                          x["policy_fidelity_review"]}, set(METHOD_GAPS))
        self.assertTrue(all(
            r["fidelity_reproduction_status"] ==
            "UNVERIFIED_SOURCE_METHOD_AND_REAL_TASK_MATCH"
            for r in x["policy_fidelity_review"]
        ))

    def test_forged_eight_policy_fidelity_approval_rejected(self):
        with self.assertRaisesRegex(ValueError, "S05"):
            self.report(0, lambda x: x.update(
                policy_implementations_faithfully_reproduced=True))

    def test_drop_or_duplicate_policy_id_rejected(self):
        for mutate in (
            lambda p: p["policy_ids"].pop(),
            lambda p: p["policy_ids"].__setitem__(0, p["policy_ids"][1]),
        ):
            with self.subTest(mutate=mutate), self.assertRaisesRegex(ValueError,"S05"):
                self.report(0, mutate)

    def test_forged_trial_completion_rejected_at_protocol(self):
        with self.assertRaisesRegex(ValueError, "S05"):
            self.report(0, lambda x: x.update(results_measured=True))

    def test_forged_lineage_split_or_admitted_task_rejected(self):
        for index, field, value, expression in (
            (2, "metadata_discovery", {"pr_leads":121}, "S06"),
            (2, "independent_pilot_admission",
             {"open_checks":0, "qualified_executable_tasks":2}, "S06"),
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, expression):
                x = list(deepcopy(self.originals))
                x[index][field] = value
                audit_remaining_stage_evidence(*x)

    def test_go_public_blueprint_cannot_admit_task(self):
        for field in ("task_admitted", "go_executed",
                      "oracle_sealed_outside_repository"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "S07"):
                self.report(4, lambda x: x.update({field:True}))

    def test_go_six_open_decisions_cannot_be_marked_reviewed(self):
        def forge(x):
            x["ambiguity_register"][0]["status"] = "APPROVED"
        with self.assertRaisesRegex(ValueError, "S07"):
            self.report(4, forge)

    def test_go_gold_output_and_removed_case_refused(self):
        for mutation in (
            lambda x: x["oracle_case_families"][0].update(
                gold_output_included=True),
            lambda x: x["oracle_case_families"].pop(),
        ):
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError,"S07"):
                self.report(4, mutation)

    def test_go_source_base_must_match_registered_candidate(self):
        with self.assertRaisesRegex(ValueError, "S07"):
            self.report(4, lambda x: x.update(base_commit="a"*40))

    def test_php_public_blueprint_cannot_self_approve_license_or_oracle(self):
        for field in ("task_admitted", "php_executed",
                      "source_file_rights_adjudicated", "original_issue_text_sealed",
                      "oracle_independently_authored"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,"S08"):
                self.report(5, lambda x: x.update({field:True}))

    def test_php_no_gold_and_no_invented_case_count(self):
        for mutation in (
            lambda x: x["oracle_case_families"][0].update(
                gold_output_included=True),
            lambda x: x["oracle_case_families"].pop(),
        ):
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError,"S08"):
                self.report(5, mutation)

    def test_model_card_tags_never_self_grant_checkpoint_approval(self):
        for field, value in (
            ("actual_qualified_checkpoints",1),
            ("full_license_reviews_completed",6),
            ("models_loaded_or_inferred",1),
            ("card_observations_authentic_signed_snapshots",True),
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,"S09"):
                self.report(3, lambda x: x.update({field:value}))

    def test_invented_model_permission_row_refused(self):
        for field in ("model_runnable_for_study",
                      "checkpoint_and_tokenizer_sha_pinned",
                      "full_license_and_access_authorized"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,"S09"):
                self.report(3, lambda x:
                            x["model_rows"][0].update({field:True}))

    def test_lost_six_model_identity_and_wrong_model_count_refused(self):
        with self.assertRaisesRegex(ValueError, "S09"):
            self.report(3, lambda x:
                        x["model_rows"][0].update(model_id="fake-model"))
        with self.assertRaisesRegex(ValueError, "S05"):
            self.report(0, lambda x: x["model_ids"].pop())

    def test_fake_paper_effect_or_overleaf_sync_rejected(self):
        for field, value, error in (
            ("measured_primary_effect", .99, "S10"),
            ("independently_qualified_real_model_runs", 2, "S10"),
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, error):
                self.report(2, lambda x: x["scientific_measurement"].update(
                    {field:value}))
        with self.assertRaisesRegex(ValueError, "S10"):
            self.report(2, lambda x: x["manuscript"].update(
                external_live_overleaf_synced=True))

    def test_main_paper_method_section_missing_refused(self):
        source=list(deepcopy(self.originals))
        source[6]=source[6].replace(
            r"\paragraph{Two-order conditional likelihood coherence (S04).}",
            "MISSING_STUDY_METHOD",
        )
        with self.assertRaisesRegex(ValueError, "S10"):
            audit_remaining_stage_evidence(*source)

    def test_critical_exit_claims_cannot_be_self_promoted(self):
        for field, value in (
            ("independently_verified_complete_exit_criteria",1),
            ("still_without_full_exit_evidence",0),
            ("overall_percent_complete",100),
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,"S10"):
                self.report(2, lambda x: x["milestone_accounting"].update(
                    {field:value}))

    def test_no_private_reviewer_signature_or_oracle_golds_in_report(self):
        report = build_remaining_stage_evidence()
        encoded=json.dumps(report,sort_keys=True)
        for disallowed in (
            "oracle_artifact_sha256", "independent_private_reviewer_signature",
            "model_access_token", "gold_output", "runtime_password",
        ):
            self.assertNotIn(disallowed,encoded)
        self.assertFalse(report["external_code_executed"])
        self.assertEqual(report["independently_authenticated_reviewer_signatures"],0)


if __name__ == "__main__":
    unittest.main()
