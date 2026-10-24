"""Task admission checks use only first-party invented fixture metadata."""
from dataclasses import replace
import unittest

from ucode.task_gate import TaskEvidence, assess_task_evidence


class TaskGateTests(unittest.TestCase):
    def setUp(self):
        self.example = TaskEvidence(
            task_id="repo_issue_1", lineage_group="upstream/project",
            cohort="naturalistic_ai_pr", repository="upstream/project",
            base_sha="a" * 40, patch_sha="b" * 40,
            changed_production_paths=("src/worker.py", "lib/client.ts"),
            claimed_changed_language="Python",
            authorship_or_generation_review_ref="reviewers/attribution-001",
            source_file_rights_review_ref="reviewers/rights-001",
            independent_oracle_review_ref="reviewers/oracle-001",
            independent_oracle_sha256="c" * 64,
            sealed_evaluator_only=True,
            image_digest="sha256:" + "d" * 64,
            runtime_nonroot=True, runtime_network_disabled=True,
            runtime_no_host_mounts=True, runtime_resource_limits=True,
        )

    def test_complete_is_still_not_verified(self):
        r = assess_task_evidence(self.example)
        self.assertEqual(r.status,
                         "declared_complete_requires_independent_verification")
        self.assertEqual(r.reasons, ())

    def test_missing_license_review_holds(self):
        r = assess_task_evidence(replace(
            self.example, source_file_rights_review_ref=""))
        self.assertEqual(r.status, "blocked")
        self.assertIn("missing_source_file_rights_review_ref", r.reasons)

    def test_wrong_github_language_does_not_relabel_patch(self):
        r = assess_task_evidence(replace(
            self.example, claimed_changed_language="Ruby"))
        self.assertIn("changed_language_mismatch", r.reasons)

    def test_fork_identity_is_required(self):
        r = assess_task_evidence(replace(self.example, lineage_group=""))
        self.assertIn("missing_lineage_group", r.reasons)

    def test_reject_docs_config_and_tests_as_production_code(self):
        for path in ("README.md", ".github/workflows/ci.yml",
                     "tests/test_worker.py", "vendor/client.py", "dist/code.js",
                     "mobile/.env.example"):
            with self.subTest(path=path):
                r = assess_task_evidence(replace(
                    self.example, changed_production_paths=(path,)))
                self.assertEqual(r.status, "blocked")

    def test_reject_path_traversal_and_absolute_files(self):
        for path in ("../outside.py", "/etc/host.py",
                     "src/../../config.py", "src\\evil.py"):
            with self.subTest(path=path):
                r = assess_task_evidence(replace(
                    self.example, changed_production_paths=(path,)))
                self.assertIn("unsafe_source_path", r.reasons)

    def test_unpinned_container_blocks(self):
        r = assess_task_evidence(replace(self.example,
                                        image_digest="python:latest"))
        self.assertIn("unpinned_container_image", r.reasons)

    def test_runtime_safety_requires_all_controls(self):
        for field in ("runtime_nonroot", "runtime_network_disabled",
                      "runtime_no_host_mounts", "runtime_resource_limits",
                      "sealed_evaluator_only"):
            with self.subTest(field=field):
                r = assess_task_evidence(replace(self.example, **{field: False}))
                self.assertIn("unsafe_or_unverified_" + field, r.reasons)

    def test_missing_oracle_hash_blocks(self):
        r = assess_task_evidence(replace(self.example,
                                        independent_oracle_sha256="unknown"))
        self.assertIn("unhashed_independent_oracle", r.reasons)

    def test_missing_oracle_review_blocks(self):
        r = assess_task_evidence(replace(self.example,
                                        independent_oracle_review_ref=""))
        self.assertIn("missing_independent_oracle_review_ref", r.reasons)

    def test_invalid_sha_and_same_base_patch(self):
        r = assess_task_evidence(replace(self.example, base_sha="recent",
                                        patch_sha="recent"))
        self.assertIn("not_immutable_base_sha", r.reasons)
        self.assertIn("patch_equal_to_base", r.reasons)

    def test_empty_and_duplicate_sources_block(self):
        empty = assess_task_evidence(replace(
            self.example, changed_production_paths=()))
        duplicate = assess_task_evidence(replace(
            self.example, changed_production_paths=("src/a.py", "src/a.py")))
        self.assertIn("missing_production_paths", empty.reasons)
        self.assertIn("duplicate_changed_paths", duplicate.reasons)

    def test_model_generation_cohort_is_not_naturalistic_pr(self):
        r = assess_task_evidence(replace(
            self.example, cohort="new_model_generation"))
        self.assertEqual(r.status,
                         "declared_complete_requires_independent_verification")
        unknown = assess_task_evidence(replace(self.example, cohort="magic"))
        self.assertIn("invalid_cohort", unknown.reasons)


if __name__ == "__main__":
    unittest.main()
