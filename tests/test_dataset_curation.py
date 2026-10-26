"""Adversarial offline tests for source-linked 120-PR metadata cleaning.

These tests cannot certify real source rights, agent line attribution,
or independent oracle correctness. They explicitly reject such promotions.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import csv
import json
import tempfile
import unittest

from scripts.summarize_audit import load_manifest, load_records
from scripts.build_clean_pr_dataset import SOURCE, AUDIT_DIR, run
from ucode.dataset_curation import (
    LANGUAGES, build_dataset, write_dataset,
)

MANIFEST = load_manifest(SOURCE)
AUDIT = load_records(AUDIT_DIR, MANIFEST)


class DatasetCleaningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cleaned = build_dataset(MANIFEST, AUDIT,
                                    sha256(SOURCE.read_bytes()).hexdigest(), 12)

    def test_count_and_original_12_language_strata(self):
        m = self.cleaned.report
        self.assertEqual(m["discovered_pr_links"], 120)
        self.assertEqual(m["distinct_repository_names"], 120)
        self.assertEqual(m["search_language_strata"], 12)
        self.assertEqual(tuple(x["search_language"]
                               for x in self.cleaned.language_summary), LANGUAGES)
        self.assertTrue(all(x["discovered_prs"] == 10
                            for x in self.cleaned.language_summary))

    def test_retrieval_failure_included_in_denominator(self):
        self.assertEqual(self.cleaned.report["metadata_retrieved"], 119)
        self.assertEqual(self.cleaned.report["metadata_not_retrieved"], 1)
        self.assertEqual(len(self.cleaned.rows), 120)

    def test_production_source_path_count_is_not_eligibility(self):
        self.assertEqual(self.cleaned.report["production_source_path_leads"], 62)
        self.assertEqual(self.cleaned.report["independently_approved_executable_tasks"], 0)
        self.assertTrue(all(r["experiment_eligible"] == "FALSE"
                            for r in self.cleaned.rows))

    def test_review_queue_is_manual_only(self):
        q = self.cleaned.review_queue
        self.assertLessEqual(len(q), 12)
        self.assertEqual(len(q), self.cleaned.report["shortlisted_for_manual_review"])
        self.assertTrue(all(r["experiment_eligible"] == "FALSE" for r in q))
        self.assertEqual(len(set(r["candidate_id"] for r in q)), len(q))

    def test_selection_deterministic_with_shuffled_audit(self):
        reversed_audit = list(reversed(AUDIT))
        a = build_dataset(MANIFEST, reversed_audit, max_review=12)
        self.assertEqual(a.rows, self.cleaned.rows)
        self.assertEqual(a.language_summary, self.cleaned.language_summary)
        self.assertEqual(a.review_queue, self.cleaned.review_queue)

    def test_language_has_changed_path_distinction(self):
        row = next(r for r in self.cleaned.rows if r["candidate_id"] == 1)
        self.assertEqual(row["search_language"], "Python")
        self.assertIn("Swift", row["observed_production_languages"])
        self.assertIn("search_language_differs", row["manual_review_reasons"])

    def test_immutable_base_and_patch_sha(self):
        source = [r for r in self.cleaned.rows
                  if r["audit_status"] == "production_source_path_detected"]
        self.assertTrue(all(len(r["base_sha"]) == 40 and
                            len(r["head_sha"]) == 40 for r in source))
        self.assertTrue(all(r["split_status"].startswith("NOT_SPLIT")
                            for r in self.cleaned.rows))

    def test_genuine_artifact_generation_without_binary_source(self):
        with tempfile.TemporaryDirectory() as d:
            hashes = write_dataset(self.cleaned, d)
            self.assertEqual(len(hashes), 4)
            csv_path = Path(d)/"clean_metadata_120.csv"
            self.assertLess(csv_path.stat().st_size, 500_000)
            with csv_path.open(encoding="utf-8", newline="") as h:
                records = list(csv.DictReader(h))
            self.assertEqual(len(records), 120)
            self.assertEqual(hashes["clean_metadata_120.csv"],
                             sha256(csv_path.read_bytes()).hexdigest())

    def test_script_reproduction_yields_4_files(self):
        with tempfile.TemporaryDirectory() as d:
            report = run(output_dir=Path(d))
            self.assertEqual(len(report["files_sha256"]), 4)
            self.assertEqual(report["metadata_retrieved"], 119)
            self.assertTrue(Path(d, "language_strata.csv").is_file())

    def test_audit_missing_entry_fails(self):
        with self.assertRaisesRegex(ValueError, "EVERY"):
            build_dataset(MANIFEST, AUDIT[:-1])

    def test_duplicate_audit_id_fails(self):
        audit = deepcopy(AUDIT)
        audit[-1]["candidate_id"] = audit[0]["candidate_id"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            build_dataset(MANIFEST, audit)

    def test_metadata_cannot_self_approve(self):
        audit = deepcopy(AUDIT)
        audit[0]["dataset_eligible"] = True
        with self.assertRaisesRegex(ValueError, "self-promote"):
            build_dataset(MANIFEST, audit)

    def test_rights_self_approval_fails(self):
        audit = deepcopy(AUDIT)
        audit[0]["rights_cleared"] = True
        with self.assertRaisesRegex(ValueError, "rights or oracle"):
            build_dataset(MANIFEST, audit)

    def test_fake_oracle_verification_fails(self):
        audit = deepcopy(AUDIT)
        audit[0]["independent_oracle_verified"] = True
        with self.assertRaisesRegex(ValueError, "rights or oracle"):
            build_dataset(MANIFEST, audit)

    def test_unsupported_external_run_claim_fails(self):
        audit = deepcopy(AUDIT)
        audit[0]["test_execution"] = "SUCCESS"
        with self.assertRaisesRegex(ValueError, "execution"):
            build_dataset(MANIFEST, audit)

    def test_forged_commit_hash_fails(self):
        audit = deepcopy(AUDIT)
        audit[0]["base_sha"] = "not-immutable"
        with self.assertRaisesRegex(ValueError, "40-hex"):
            build_dataset(MANIFEST, audit)

    def test_pr_url_repository_identity_check(self):
        manifest = deepcopy(MANIFEST)
        manifest[1]["agent_pr_url"] = "https://github.com/wrong/other/pull/1"
        audit = deepcopy(AUDIT)
        audit[0]["pr_url"] = manifest[1]["agent_pr_url"]
        with self.assertRaisesRegex(ValueError, "URL"):
            build_dataset(manifest, audit)

    def test_group_split_not_falsely_frozen(self):
        self.assertTrue(all(r["lineage_group_review"] == "PENDING_INDEPENDENT_REVIEW"
                            for r in self.cleaned.rows))
        self.assertFalse(self.cleaned.report["independent_train_test_split_frozen"])

    def test_in_repo_snapshot_matches_recomputed_canonical_data(self):
        root = Path(__file__).resolve().parents[1]
        saved = json.loads((root / "data/curated/2026-10-27/"
                            "frozen_cleaning_summary.json").read_text(
                                encoding="utf-8"))
        current = self.cleaned.report
        for name in ("discovered_pr_links", "distinct_repository_names",
                     "metadata_retrieved", "production_source_path_leads",
                     "first_pass_manual_review_leads",
                     "shortlisted_for_manual_review",
                     "independently_approved_executable_tasks",
                     "discovery_manifest_sha256", "status_counts"):
            with self.subTest(name=name):
                self.assertEqual(saved[name], current[name])
        for actual, pinned in zip(current["by_search_language"],
                                  saved["by_search_language"]):
            for name, value in pinned.items():
                self.assertEqual(actual[name], value)

    def test_review_budget_zero_disables_shortlist_only(self):
        x = build_dataset(MANIFEST, AUDIT, max_review=0)
        self.assertEqual(len(x.rows), 120)
        self.assertEqual(len(x.review_queue), 0)
        self.assertEqual(x.report["independently_approved_executable_tasks"], 0)


if __name__ == "__main__":
    unittest.main()
