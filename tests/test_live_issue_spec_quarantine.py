"""Source-era adversarial regression tests; no third-party code and no gold."""
from copy import deepcopy
from pathlib import Path
import json
import unittest
from ucode.live_issue_spec_quarantine import audit_live_issue_observations

ROOT = Path(__file__).resolve().parents[1]

class LiveIssueQuarantineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads((ROOT / "data/admission/2026-10-29/live_issue_current_body_review_metadata.json").read_text("utf-8"))
        cls.chronology = json.loads((ROOT / "data/admission/2026-10-27/two_candidate_issue_chronology_metadata.json").read_text("utf-8"))

    def check(self, audit=None, chronology=None):
        return audit_live_issue_observations(self.audit if audit is None else audit,
                                              self.chronology if chronology is None else chronology)

    def test_both_live_issue_texts_are_quarantined(self):
        x = self.check()
        self.assertEqual(x["eligible_real_tasks"], 0)
        self.assertEqual(x["historical_issue_body_snapshots_verified"], 0)
        self.assertEqual(x["independent_functional_oracles_verified"], 0)
        self.assertEqual(x["external_code_executions"], 0)
        self.assertEqual([r["candidate_id"] for r in x["records"]], [43, 104])
        self.assertEqual([r["issue_to_pr_seconds"] for r in x["records"]], [8, 152])
        self.assertTrue(all(r["issue_text_as_of_pr"] == "NOT_PROVEN" for r in x["records"]))
        self.assertTrue(all(not r["policy_input_eligible"] for r in x["records"]))

    def test_recent_updated_time_does_not_prove_body_changed(self):
        self.assertTrue(all(x["current_issue_updated_after_pr"] for x in self.check()["records"]))

    def test_cannot_inject_issue_body_or_solution(self):
        for key in ("body", "original_issue_body", "solution_patch", "gold_test",
                    "right_answer", "upstream_edit_history"):
            x = deepcopy(self.audit)
            x["records"][0][key] = "POSTFIX"
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "leakage"):
                self.check(x)

    def test_self_approval_fails_closed(self):
        for flag in ("body_text_stored", "original_body_verified",
                     "independent_spec_approval", "task_admitted"):
            x = deepcopy(self.audit)
            x["records"][0][flag] = True
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, "self-authorize"):
                self.check(x)

    def test_wrong_repository_or_issue_rejected(self):
        for field in ("repository", "issue_url"):
            x = deepcopy(self.audit)
            x["records"][0][field] = "https://example.invalid"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "identity"):
                self.check(x)

    def test_pr_era_current_issue_cannot_masquerade_as_archive(self):
        x = deepcopy(self.audit)
        x["records"][0]["source_kind"] = "IMMUTABLE_ISSUE_ORIGINAL"
        with self.assertRaisesRegex(ValueError, "not an immutable"):
            self.check(x)

    def test_future_issue_or_invalid_updated_order(self):
        x = deepcopy(self.audit)
        x["records"][0]["observed_issue_updated_at"] = "2026-10-30T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "chronology"):
            self.check(x)

    def test_cannot_backdate_present_observation(self):
        x = deepcopy(self.audit)
        x["records"][0]["observed_at"] = "2026-10-23T12:18:49Z"
        with self.assertRaises(ValueError):
            self.check(x)

    def test_bad_timestamps_rejected(self):
        for value in ("2026-10-29T09:00:00", "not-time", "2026-10-29T09:00Z",
                      "2026-10-29T09:00:00+00:00", 45, True):
            x = deepcopy(self.audit)
            x["records"][0]["observed_at"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.check(x)

    def test_duplicate_and_missing_candidates_rejected(self):
        x = deepcopy(self.audit)
        x["records"][1] = deepcopy(x["records"][0])
        with self.assertRaisesRegex(ValueError, "repeated"):
            self.check(x)
        x["records"] = x["records"][:1]
        with self.assertRaisesRegex(ValueError, "exactly two"):
            self.check(x)

    def test_chronology_sha_independent_source_check_still_required(self):
        # Negative stage cannot upgrade even if attacker edits unrelated fields.
        x = deepcopy(self.chronology)
        x["records"][0]["pr_created_at"] = "2026-10-23T12:18:49Z"
        with self.assertRaisesRegex(ValueError, "did not precede"):
            self.check(chronology=x)

    def test_row_reordering_does_not_change_report(self):
        x = deepcopy(self.audit)
        x["records"].reverse()
        self.assertEqual(self.check(), self.check(audit=x))

if __name__ == "__main__":
    unittest.main()
