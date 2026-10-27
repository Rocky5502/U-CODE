"""Adversarial no-execution verification of two public issue-event windows."""
from copy import deepcopy
from pathlib import Path
import json
import unittest

from ucode.issue_event_window_audit import verify_issue_event_windows
from ucode.pending_review_packets import create_pending_review_packets

ROOT = Path(__file__).resolve().parents[1]
ISSUES = ROOT / "data/admission/2026-10-27/two_candidate_issue_chronology_metadata.json"
EVENTS = ROOT / "data/admission/2026-10-28/two_candidate_issue_event_first_pages.json"


class EventWindowAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.event_data = json.loads(EVENTS.read_text("utf-8"))
        cls.issue_data = json.loads(ISSUES.read_text("utf-8"))
        cls.packets = create_pending_review_packets()[0]

    def check(self, events=None, issues=None):
        return verify_issue_event_windows(
            self.event_data if events is None else events,
            self.issue_data if issues is None else issues,
            self.packets,
        )

    def test_actual_first_pages_do_not_qualify_real_tasks(self):
        r = self.check()
        self.assertEqual(r["qualified_executable_tasks"], 0)
        self.assertEqual(r["issue_body_at_pr_creation_verified"], 0)
        self.assertEqual(r["source_page_completeness"], "NOT_ATTESTED")
        self.assertFalse(r["external_code_executed"])
        by_id = {x["candidate_id"]: x for x in r["records"]}
        self.assertEqual(by_id[104]["observed_pre_pr_events"], 3)
        self.assertEqual(by_id[104]["observed_post_or_at_pr_events"], 2)
        self.assertEqual(by_id[43]["observed_pre_pr_events"], 2)
        self.assertEqual(by_id[43]["observed_post_or_at_pr_events"], 2)
        self.assertEqual({k: v["pre_pr_lead_seconds"] for k,v in by_id.items()},
                         {43:8,104:152})

    def test_event_absence_is_not_issue_body_proof(self):
        r = self.check()
        self.assertTrue(all(x["issue_body_at_pr_creation"] ==
                            "NOT_VERIFIED_BY_EVENT_API" for x in r["records"]))
        self.assertTrue(all("edited" not in x["pre_pr_event_types"]
                            for x in r["records"]))

    def test_reject_injected_oracle_or_patch_in_event(self):
        for key in ("hidden_test", "gold_patch", "is_correct", "body", "actor"):
            x = deepcopy(self.event_data)
            x["records"][0]["events"][0][key] = "spoiler"
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "gold leakage"):
                self.check(x)

    def test_reject_injected_review_or_approval_field(self):
        for key in ("task_approved", "reviewer", "gold_label"):
            x = deepcopy(self.event_data)
            x["records"][0][key] = True
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "policy/oracle leakage"):
                self.check(x)

    def test_self_approved_boolean_cannot_promote(self):
        for key in ("full_history_verified", "issue_body_snapshot_verified", "task_admitted"):
            x = deepcopy(self.event_data)
            x["records"][0][key] = True
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "cannot self-certify"):
                self.check(x)

    def test_duplicate_and_noninteger_event_ids_rejected(self):
        for bad in (True, -1, "34001095385", self.event_data["records"][0]["events"][1]["event_id"]):
            x = deepcopy(self.event_data)
            x["records"][0]["events"][0]["event_id"] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "event ID"):
                self.check(x)

    def test_duplicate_candidate_rejected(self):
        x = deepcopy(self.event_data)
        x["records"][1] = deepcopy(x["records"][0])
        with self.assertRaisesRegex(ValueError, "candidate ID"):
            self.check(x)

    def test_wrong_issue_and_api_url_rejected(self):
        for key in ("issue_url","events_api_url","repository"):
            x = deepcopy(self.event_data)
            x["records"][0][key] = "https://evil.invalid/other"
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "disagrees"):
                self.check(x)

    def test_timestamp_order_and_pre_creation_rejected(self):
        for value in ("2026-10-22T22:53:09Z", "2026-10-21T00:00:00Z"):
            x = deepcopy(self.event_data)
            x["records"][0]["events"][0]["created_at"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "precedes"):
                self.check(x)
        x = deepcopy(self.event_data)
        x["records"][0]["events"][1]["created_at"] = "2026-10-22T22:53:09Z"
        with self.assertRaisesRegex(ValueError, "out of order|precedes"):
            self.check(x)

    def test_unbounded_or_empty_event_page_rejected(self):
        for entries in ([], [self.event_data["records"][0]["events"][0]]*101):
            x = deepcopy(self.event_data)
            x["records"][0]["events"] = entries
            with self.assertRaisesRegex(ValueError, "bounded first page"):
                self.check(x)

    def test_naive_future_or_nonsense_date_rejected(self):
        for value in ("2026-10-22T22:53:12", "invalid", 42):
            x = deepcopy(self.event_data)
            x["records"][0]["events"][0]["created_at"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.check(x)
        x = deepcopy(self.event_data)
        x["records"][0]["events"][-1]["created_at"] = "2026-11-01T23:00:00Z"
        with self.assertRaisesRegex(ValueError, "after stated observation"):
            self.check(x)

    def test_page_size_cannot_claim_total_completeness(self):
        for bad in (0, 200, True):
            x = deepcopy(self.event_data)
            x["records"][0]["page_size"] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "page size"):
                self.check(x)

    def test_issue_chronology_integrity_checked_upstream(self):
        x = deepcopy(self.issue_data)
        x["records"][0]["pr_base_sha"] = "f"*40
        with self.assertRaisesRegex(ValueError, "immutable PR SHA"):
            self.check(issues=x)


if __name__ == "__main__":
    unittest.main()
