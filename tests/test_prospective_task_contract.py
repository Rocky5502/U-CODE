"""First-party PHP #104 prospective draft checks; NO PHP execution or gold."""
from dataclasses import replace
from pathlib import Path
import json
import unittest

from scripts.validate_php104_prospective_draft import (
    DEFAULT_DRAFT, DEFAULT_SOURCE, validate_pending_php104_draft,
)
from ucode.prospective_task_contract import (
    ObservedSourceBlob, parse_prospective_review_draft,
    validate_php104_prospective_draft,
)


class ProspectiveDraftReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=json.loads(Path(DEFAULT_DRAFT).read_text("utf-8"))
        cls.source=json.loads(Path(DEFAULT_SOURCE).read_text("utf-8"))
        cls.draft=parse_prospective_review_draft(cls.raw)

    def test_public_proposal_is_different_from_historical_task(self):
        result=validate_pending_php104_draft()
        self.assertEqual(result["namespace"],"prospective:source-lead:104")
        self.assertIn("NOT_POLICY_INPUT",result["stage"])
        self.assertFalse(result["historical_task_eligible"])
        self.assertFalse(result["prospective_task_eligible"])
        self.assertFalse(result["coding_agent_policy_input_approved"])
        self.assertFalse(result["hidden_oracle_authored"])
        self.assertEqual(result["real_repository_executions"],0)
        self.assertEqual(result["read_only_source_observation_leads"],5)

    def test_public_draft_hash_is_stable_and_content_sensitive(self):
        canonical=self.draft.public_draft_sha256
        self.assertEqual(canonical,parse_prospective_review_draft(
            dict(reversed(list(self.raw.items())))).public_draft_sha256)
        changed=replace(self.draft,requirement_statements=(
            self.draft.requirement_statements[0]+" Added future reviewer question.",
            *self.draft.requirement_statements[1:]))
        self.assertNotEqual(changed.public_draft_sha256,canonical)
        self.assertEqual(len(canonical),64)

    def test_all_self_approval_bools_rejected_even_if_only_one_changed(self):
        flags=(
            "historical_original_issue_body_attested",
            "proposed_spec_independently_reviewed",
            "file_reuse_rights_cleared",
            "hidden_oracle_independently_sealed",
            "toolchain_verified",
            "runner_physically_attested",
            "five_resource_meters_attested",
            "third_party_code_executed",
            "experiment_eligible",
        )
        for name in flags:
            with self.subTest(name=name),self.assertRaisesRegex(
                    ValueError,"cannot claim"):
                parse_prospective_review_draft(dict(self.raw,**{name:True}))

    def test_no_extra_solution_or_gold_fields_allowed(self):
        for field in ("gold_patch","FAIL_TO_PASS","oracle_passed",
                      "head_sha","post_fix_solution","pr_authored_tests",
                      "coding_agent_prompt","independent_approval"):
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"exact safe"):
                parse_prospective_review_draft(dict(self.raw,**{field:"unsafe"}))

    def test_no_extra_source_observation_label_allowed(self):
        x=json.loads(json.dumps(self.raw))
        x["source_observations"][0]["expected_output"]="private"
        with self.assertRaisesRegex(ValueError,"forbids solution"):
            parse_prospective_review_draft(x)

    def test_pre_fix_blob_mismatch_is_detected(self):
        changed=replace(self.draft,source_observations=(
            replace(self.draft.source_observations[0],git_blob_sha="a"*40),
            *self.draft.source_observations[1:]))
        with self.assertRaisesRegex(ValueError,"changed pinned pre-fix"):
            validate_php104_prospective_draft(changed,self.source)

    def test_post_fix_file_cannot_be_substituted_for_pre_fix_source(self):
        changed=replace(self.draft,source_observations=(
            replace(self.draft.source_observations[0],
                    path="src/PersistenceHandler/FilePersistenceLayout.php"),
            *self.draft.source_observations[1:]))
        with self.assertRaisesRegex(ValueError,"changed pinned pre-fix"):
            validate_php104_prospective_draft(changed,self.source)

    def test_no_traversal_or_control_bytes_in_source_file_paths(self):
        original=self.draft.source_observations[0]
        for bad in ("../secret.php","/tmp/gold.php","src/../secret.php",
                    "src//config.php","C:/private.txt","src\\wrong.php"):
            with self.subTest(bad=bad), self.assertRaisesRegex(
                    ValueError,"invalid relative"):
                replace(original,path=bad)

    def test_proposal_cannot_be_backdated_to_pre_pr_time(self):
        with self.assertRaisesRegex(ValueError,"creation before"):
            validate_php104_prospective_draft(
                replace(self.draft,proposal_creation_date="2026-10-22"),
                self.source)

    def test_historical_id_cannot_masquerade_as_prospective(self):
        with self.assertRaisesRegex(ValueError,"separate namespace"):
            replace(self.draft,task_namespace="historical:104")
        with self.assertRaisesRegex(ValueError,"separate namespace"):
            replace(self.draft,task_namespace="prospective:source-lead:43")

    def test_changed_source_parent_identity_invalidates_crosswalk(self):
        altered=dict(self.source,candidate_id=43)
        with self.assertRaisesRegex(ValueError,"identity mismatch"):
            validate_php104_prospective_draft(self.draft,altered)

    def test_unapproved_promotion_not_in_derived_summary(self):
        summary=self.draft.review_summary()
        for name in ("policy_prompt","evaluator_only_gold","hidden_tests",
                     "agent_task_view","approval_signature"):
            self.assertNotIn(name,summary)
        self.assertFalse(any(summary[k] for k in (
            "historical_task_eligible","prospective_task_eligible",
            "coding_agent_policy_input_approved")))

    def test_public_requirements_are_bounded_and_review_only(self):
        with self.assertRaisesRegex(ValueError,"malformed/newline"):
            replace(self.draft,requirement_statements=(
                "Unapproved expected output: gold\nprivate",
                *self.draft.requirement_statements[1:]))
        with self.assertRaisesRegex(ValueError,"bounded"):
            replace(self.draft,requirement_statements=())

    def test_all_original_leads_are_accounted_for_exactly(self):
        r=validate_php104_prospective_draft(self.draft,self.source)
        self.assertEqual(r["read_only_source_observation_leads"],
                         len(self.source["source_observations"]))
        self.assertEqual(len(self.draft.source_observations),
                         len(set(x.observation_id
                                 for x in self.draft.source_observations)))


if __name__=="__main__":
    unittest.main()
