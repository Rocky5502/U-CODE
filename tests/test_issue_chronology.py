"""Evidence that PRE-PR issue creation alone does NOT verify pre-PR text."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from ucode.pending_review_packets import create_pending_review_packets
from ucode.issue_chronology import verify_issue_prepr_chronology

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/admission/2026-10-27/two_candidate_issue_chronology_metadata.json"


class IssueChronologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text("utf-8"))
        cls.packets = create_pending_review_packets()[0]

    def check(self, source=None):
        return verify_issue_prepr_chronology(
            self.source if source is None else source, self.packets)

    def test_two_real_source_issues_predate_pr_but_body_not_verified(self):
        result = self.check()
        self.assertEqual(result["source_issue_created_before_pr"], 2)
        self.assertEqual(result["issue_body_time_travel_verified"], 0)
        self.assertEqual(result["qualified_executable_tasks"], 0)
        leads = {r["candidate_id"]: r["lead_time_seconds"] for r in result["records"]}
        self.assertEqual(leads, {43: 8, 104: 152})

    def test_short_issue_window_is_high_priority_manual_review(self):
        result = self.check()
        by_id = {r["candidate_id"]: r for r in result["records"]}
        self.assertEqual(
            by_id[43]["review_priority"],
            "VERY_SHORT_PREPR_WINDOW_MANUAL_CONTEXT_CHECK")
        self.assertEqual(
            by_id[104]["review_priority"],
            "TASK_ERA_BODY_VERSION_HISTORY_REVIEW")

    def test_post_pr_issue_updates_not_claimed_as_original_spec(self):
        result = self.check()
        self.assertTrue(all(
            r["source_body_unchanged_at_pr_creation"] == "UNVERIFIED"
            for r in result["records"]))

    def test_reverse_temporal_claim_fails(self):
        x = deepcopy(self.source)
        x["records"][0]["issue_created_at"] = "2026-10-24T22:53:10Z"
        x["records"][0]["issue_updated_at"] = "2026-10-24T22:53:10Z"
        with self.assertRaisesRegex(ValueError, "after PR"):
            self.check(x)

    def test_pr_base_sha_must_equal_original_dossier(self):
        x = deepcopy(self.source)
        x["records"][0]["pr_base_sha"] = "f"*40
        with self.assertRaisesRegex(ValueError, "immutable PR SHA"):
            self.check(x)

    def test_cannot_inject_gold_labels_in_issue_metadata(self):
        x = deepcopy(self.source)
        x["records"][0]["gold_patch"] = "hidden"
        with self.assertRaisesRegex(ValueError, "oracle leakage"):
            self.check(x)

    def test_cannot_self_approve_original_issue_body(self):
        x = deepcopy(self.source)
        x["records"][0]["issue_text_at_pr_creation_immutably_archived"] = True
        with self.assertRaisesRegex(ValueError, "cannot self-promote"):
            self.check(x)

    def test_no_fake_oracle_or_rights_approval(self):
        for field in ("independent_oracle_verified", "source_rights_verified",
                      "executable_task_approved"):
            x = deepcopy(self.source)
            x["records"][0][field] = True
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "cannot self-promote"):
                    self.check(x)

    def test_timezone_naive_timestamps_rejected(self):
        x = deepcopy(self.source)
        x["records"][0]["issue_created_at"] = "2026-10-22T22:53:10"
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            self.check(x)

    def test_issue_link_cannot_point_to_post_pr_pull_request(self):
        x = deepcopy(self.source)
        x["records"][0]["issue_url"] = x["records"][0]["pr_url"]
        with self.assertRaisesRegex(ValueError, "identity"):
            self.check(x)

    def test_duplicate_candidate_fails_closed(self):
        x = deepcopy(self.source)
        x["records"][1] = deepcopy(x["records"][0])
        with self.assertRaisesRegex(ValueError, "unique canonical"):
            self.check(x)

    def test_issue_updated_cannot_predate_creation(self):
        x = deepcopy(self.source)
        x["records"][0]["issue_updated_at"] = "2026-10-21T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "before issue creation"):
            self.check(x)


if __name__ == "__main__":
    unittest.main()
