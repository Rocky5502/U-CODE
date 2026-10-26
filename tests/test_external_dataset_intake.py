"""Synthetic intake tests: safety separation from upstream gold/test patches."""
import unittest

from ucode.external_dataset_intake import (
    csv_release, read_local_parquet_projected, screen_swe_rebench_v2,
)

REV = "a"*40
SHA = "b"*40


def row(uid, repo="test/repo", lang="py", license_id="MIT", **overrides):
    data = {"instance_id": uid, "repo": repo,
            "base_commit": SHA, "language": lang,
            "license": license_id, "created_at": "2025-01-01",
            "image_name": "untrusted/not-executed:1"}
    data.update(overrides)
    return data


class ExternalIntakeTests(unittest.TestCase):
    def test_two_languages_normalized_without_gold(self):
        x = screen_swe_rebench_v2([row("1", lang="ts"),
                                   row("2", lang="C++")], revision=REV)
        self.assertEqual(x.report["metadata_candidate_rows_kept"], 2)
        self.assertEqual(x.report["kept_by_normalized_language"],
                         {"C++": 1, "TypeScript": 1})
        self.assertFalse(x.report["evaluation_gold_or_test_patches_exposed"])
        self.assertTrue(all(v["experiment_eligible"] == "FALSE"
                            for v in x.candidates))

    def test_all_12_languages_supported(self):
        labels = ("python", "js", "ts", "java", "go", "rust",
                  "c++", "c", "c#", "kotlin", "php", "ruby")
        records = [row(str(i), lang=lang) for i, lang in enumerate(labels)]
        out = screen_swe_rebench_v2(records, revision=REV)
        self.assertEqual(len(out.report["kept_by_normalized_language"]), 12)

    def test_upstream_20_language_dataset_out_of_scope_retained_as_attrition(self):
        x = screen_swe_rebench_v2(
            [row("excluded", lang="Julia"), row("kept", lang="Java")],
            revision=REV)
        self.assertEqual(x.report["rows_scanned_in_LOCAL_snapshot"], 2)
        self.assertEqual(x.report["metadata_candidate_rows_kept"], 1)
        self.assertEqual(x.report["excluded_metadata_rows"], 1)

    def test_no_gold_oracle_or_pr_content_can_be_ingested(self):
        for name in ("patch", "test_patch", "FAIL_TO_PASS",
                     "PASS_TO_PASS", "meta", "pr_description",
                     "problem_statement", "install_config"):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "gold/test patch"):
                    screen_swe_rebench_v2([row("u", **{name: "GOLD"})],
                                          revision=REV)

    def test_40hex_dataset_source_required(self):
        with self.assertRaisesRegex(ValueError, "40-hex"):
            screen_swe_rebench_v2([row("u")], revision="main")

    def test_duplicate_source_instance_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate instance"):
            screen_swe_rebench_v2([row("same"), row("same")], revision=REV)

    def test_bogus_repository_or_sha_is_excluded_not_silent(self):
        result = screen_swe_rebench_v2(
            [row("bad-repo", repo="bad"), row("badsha", base_commit="main"),
             row("valid")], revision=REV)
        self.assertEqual(result.report["excluded_metadata_rows"], 2)
        self.assertEqual(result.report["metadata_candidate_rows_kept"], 1)

    def test_shared_repo_base_is_warning_not_deleted(self):
        x = screen_swe_rebench_v2([row("1"), row("2")], revision=REV)
        self.assertEqual(len(x.candidates), 2)
        self.assertTrue(all(v["same_base_commit_cluster_hint"].startswith(
            "CANDIDATE_SHARED_BASE_REVIEW") for v in x.candidates))
        self.assertFalse(x.report["train_test_split_adjudicated"])

    def test_source_repo_name_overlap_not_proven_content_leak(self):
        x = screen_swe_rebench_v2(
            [row("1", repo="test/repo"), row("2", repo="other/repo")],
            revision=REV, existing_discovery_repositories=["Test/Repo"])
        self.assertEqual(x.report["potential_source_repo_name_overlap_count"], 1)
        self.assertTrue(any(v["related_to_existing_discovery_repo"]
                            == "POTENTIAL_OVERLAP_REVIEW"
                            for v in x.candidates))

    def test_missing_repo_license_is_unapproved_exclusion(self):
        x = screen_swe_rebench_v2([row("1", license_id="")], revision=REV)
        self.assertEqual(x.report["metadata_candidate_rows_kept"], 0)
        self.assertEqual(x.report["excluded_metadata_rows"], 1)

    def test_unknown_columns_rejected_to_prevent_leakage(self):
        with self.assertRaisesRegex(ValueError, "exact seven"):
            screen_swe_rebench_v2([row("1", unexpected="hi")], revision=REV)

    def test_output_only_public_metadata_and_no_oracle_fields(self):
        data = screen_swe_rebench_v2([row("1")], revision=REV)
        csvdata = csv_release(data)
        self.assertIn("external_instance_id", csvdata)
        self.assertNotIn("FAIL_TO_PASS", csvdata)
        self.assertNotIn("patch", csvdata.lower())
        self.assertIn("NOT_RUN", csvdata)

    def test_no_inference_or_qualified_task_claim(self):
        r = screen_swe_rebench_v2([row("1")], revision=REV).report
        self.assertFalse(r["sealed_oracles_verified"])
        self.assertFalse(r["model_inference_executed"])
        self.assertEqual(r["independent_executable_task_admissions"], 0)

    def test_invalid_parquet_batch_size_fails_without_dependency(self):
        with self.assertRaisesRegex(ValueError, "batch size"):
            list(read_local_parquet_projected([], batch_size=0))


if __name__ == "__main__":
    unittest.main()
