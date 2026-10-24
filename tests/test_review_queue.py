"""Auditable manual triage: source paths are never admitted experiments."""
from dataclasses import replace
import csv
import io
import unittest

from scripts.summarize_audit import load_manifest, load_records
from scripts.triage_review_queue import output_csv
from ucode.review_queue import rank_candidate, select_review_queue


def fixture(**changes):
    d = {
        "candidate_id": 999, "repository": "example/project",
        "pr_url": "https://github.com/example/project/pull/1",
        "discovery_language": "Python",
        "triage_status": "production_source_path_detected",
        "production_files": ["src/worker.py"],
        "test_files": ["tests/test_worker.py"],
        "github_changed_file_count": 2,
        "repository_license_spdx": "MIT", "fork": False,
        "changed_file_list_complete": True, "dataset_eligible": False,
    }
    return {**d, **changes}


class ManualLeadQueueTests(unittest.TestCase):
    def test_first_pass_is_only_a_manual_review_queue(self):
        result = rank_candidate(fixture())
        self.assertEqual(result.priority_class, "first_pass_manual_review")
        self.assertFalse(result.eligible)
        self.assertIn("ai_line_authorship_unverified", result.reasons)
        self.assertIn("oracle_not_qualified", result.reasons)

    def test_no_source_status_promoted_to_source_review(self):
        for status in ("retrieval_failed", "test_only_source_change",
                       "non_source_change", "empty_file_list_needs_review"):
            with self.subTest(status=status):
                self.assertIsNone(rank_candidate(fixture(triage_status=status)))

    def test_unknown_license_deprioritized(self):
        result = rank_candidate(fixture(repository_license_spdx=None))
        self.assertEqual(result.priority_class, "second_pass_manual_review")
        self.assertIn("repository_spdx_unknown", result.reasons)

    def test_security_and_generated_content_deprioritized(self):
        for path in ("src/auth/login.py", "vendor/wordlist.py",
                     "src/generated_dispatch.py"):
            with self.subTest(path=path):
                result = rank_candidate(fixture(production_files=[path]))
                self.assertEqual(result.priority_class, "second_pass_manual_review")

    def test_no_tests_large_change_or_fork_deprioritized(self):
        for changes in ({"test_files": []}, {"fork": True},
                        {"github_changed_file_count": 100}):
            with self.subTest(changes=changes):
                self.assertEqual(rank_candidate(fixture(**changes)).priority_class,
                                 "second_pass_manual_review")

    def test_incomplete_changed_filenames_never_first_pass(self):
        result = rank_candidate(fixture(changed_file_list_complete=False))
        self.assertEqual(result.priority_class, "second_pass_manual_review")

    def test_duplicate_record_or_invalid_path_count_fails(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            select_review_queue([fixture(), fixture()])
        with self.assertRaisesRegex(ValueError, "implausible"):
            rank_candidate(fixture(github_changed_file_count=0))

    def test_full_120_metadata_screen_yields_62_noneligible_manual_leads(self):
        manifest = load_manifest("data/discovery/agent_pr_candidates_120.csv")
        records = load_records("data/audits/2026-10-24", manifest)
        q = select_review_queue(records)
        self.assertEqual(len(q), 62)
        self.assertEqual({x.candidate_id for x in q},
                         {x["candidate_id"] for x in records
                          if x["triage_status"] == "production_source_path_detected"})
        self.assertTrue(all(not x.eligible and x.reasons for x in q))
        self.assertTrue(all(q[i].priority_class == "first_pass_manual_review"
                            or q[i+1].priority_class == "second_pass_manual_review"
                            for i in range(len(q)-1)))

    def test_csv_explicitly_marks_every_row_not_eligible(self):
        text = output_csv(select_review_queue([fixture()]))
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["eligible"], "FALSE")


if __name__ == "__main__":
    unittest.main()
