"""Canonical 120-PR metadata screen acceptance tests (NOT study eligibility)."""
from collections import Counter
import unittest

from scripts.summarize_audit import load_manifest, load_records, summarize

ROOT = "data/audits/2026-10-24"
MANIFEST = "data/discovery/agent_pr_candidates_120.csv"


class CompleteDiscoveryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest(MANIFEST)
        cls.records = load_records(ROOT, cls.manifest)
        cls.stats = summarize(cls.records, cls.manifest)

    def test_all_discovered_ids_accounted_exactly_once(self):
        self.assertEqual(len(self.manifest), 120)
        self.assertEqual(len(self.records), 120)
        self.assertEqual({int(r["candidate_id"]) for r in self.records},
                         set(self.manifest))

    def test_twelve_primary_language_strata_each_have_ten_leads(self):
        self.assertEqual(sorted(Counter(
            x["discovery_language"] for x in self.records).values()),
            [10] * 12)

    def test_all_links_attempted_and_one_recorded_retrieval_failure(self):
        self.assertEqual(self.stats["discovery_links_attempted"], 120)
        self.assertEqual(self.stats["metadata_retrieved"], 119)
        self.assertEqual(self.stats["metadata_retrieval_failed"], 1)
        self.assertEqual(self.stats["unattempted_manifest_links"], 0)
        self.assertEqual(self.stats["retrieval_failure_candidate_ids"], [26])

    def test_honest_attrition_not_redefined_as_verified_dataset(self):
        expected = {
            "production_source_path_detected": 62,
            "test_only_source_change": 10,
            "non_source_change": 45,
            "empty_file_list_needs_review": 2,
            "retrieval_failed": 1,
        }
        self.assertEqual(self.stats["source_status_counts"], expected)
        self.assertEqual(sum(expected.values()), 120)
        self.assertEqual(self.stats["independently_eligible_units"], 0)

    def test_repo_license_counts_not_confused_with_file_rights(self):
        self.assertEqual(self.stats["recognized_repository_spdx"], 62)
        self.assertEqual(self.stats["unknown_or_noassertion_repository_spdx"], 57)
        self.assertEqual(self.stats["forks"], 12)
        self.assertEqual(self.stats["missing_immutable_sha_candidate_ids"], [])

    def test_new_tenth_stratum_preserves_no_oracle_execution(self):
        for r in self.records:
            if int(r["candidate_id"]) % 10 != 0:
                continue
            self.assertFalse(r["dataset_eligible"])
            self.assertNotEqual(r.get("test_execution"), "VERIFIED")
            self.assertNotEqual(r.get("agent_line_attribution"), "confirmed")
            if r["triage_status"] != "retrieval_failed":
                self.assertTrue(r.get("base_sha"))
                self.assertTrue(r.get("head_sha"))
                self.assertTrue(r.get("merge_commit_sha"))

    def test_tenth_stratum_filenames_are_complete_except_explicit_reviews(self):
        for r in self.records:
            if int(r["candidate_id"]) % 10 != 0:
                continue
            self.assertIs(r["changed_file_list_complete"], True)
            if r["triage_status"] != "empty_file_list_needs_review":
                self.assertEqual(
                    len(r["changed_paths"]), r["github_changed_file_count"])


if __name__ == "__main__":
    unittest.main()
