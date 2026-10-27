"""Adversarial offline PHP #104 parent/source-era evidence tests.

No PHP code, external dependency or real repository is executed.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from ucode.php104_source_contract_audit import verify_php104_source_contract_leads

ROOT = Path(__file__).resolve().parents[1]
ADMISSION = ROOT / "data/admission"
LEDGER = ADMISSION / "2026-10-28/php104_base_source_contract_leads.json"
CHRONOLOGY = ADMISSION / "2026-10-27/two_candidate_issue_chronology_metadata.json"
TREES = ADMISSION / "2026-10-27/two_candidate_pre_fix_tree_inventory.json"
DOSSIERS = ADMISSION / "2026-10-25/pilot_dossiers.jsonl"


class PHP104SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text("utf-8"))
        cls.chronology = json.loads(CHRONOLOGY.read_text("utf-8"))
        cls.trees = json.loads(TREES.read_text("utf-8"))
        cls.dossiers = [json.loads(s) for s in DOSSIERS.read_text("utf-8").splitlines() if s.strip()]

    def check(self, x=None, chronology=None, trees=None):
        return verify_php104_source_contract_leads(
            self.ledger if x is None else x,
            self.chronology if chronology is None else chronology,
            self.trees if trees is None else trees,
            self.dossiers,
        )

    def test_real_parent_child_pr_are_observed_but_not_admitted(self):
        r = self.check()
        self.assertEqual((r["parent_created_before_child_seconds"],
                          r["parent_created_before_pr_seconds"],
                          r["child_created_before_pr_seconds"]), (70, 222, 152))
        self.assertEqual(r["read_only_source_observation_leads"], 5)
        self.assertEqual(r["distinct_pinned_pre_fix_blobs"], 4)
        self.assertEqual(r["executable_tasks_admitted"], 0)
        self.assertEqual(r["independent_functional_oracles_verified"], 0)
        self.assertTrue(r["never_agent_visible"])
        self.assertFalse(r["original_issue_body_at_pr_creation_verified"])
        self.assertFalse(r["third_party_code_executed"])

    def test_reviewer_metadata_must_not_reach_agent_or_oracle(self):
        for field in ("hidden_tests", "gold_patch", "solution", "reviewer_signed",
                      "issue_body", "pr_head_sha", "approved"):
            x = deepcopy(self.ledger)
            x[field] = "untrusted"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "unexpected PHP"):
                self.check(x)

    def test_parent_issue_body_never_self_attests(self):
        for field in ("parent_issue_body_at_pr_time_archived",
                      "independent_pre_fix_task_spec_approved",
                      "source_rights_cleared", "held_out_oracle_approved",
                      "third_party_code_executed", "executable_task_admitted"):
            x = deepcopy(self.ledger)
            x[field] = True
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "cannot self-approve"):
                self.check(x)

    def test_unauthenticated_parent_issue_identity_rejected(self):
        for field in ("parent_issue_url", "repository", "child_issue_url",
                      "base_commit", "base_tree_sha"):
            x = deepcopy(self.ledger)
            x[field] = "https://example.invalid/tampered"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "identity mismatch"):
                self.check(x)

    def test_swapped_source_blob_and_path_rejected(self):
        for field, value in (("path", "src/PersistenceHandler/FilePersistenceLayout.php"),
                             ("git_blob_sha", "a"*40)):
            x = deepcopy(self.ledger)
            x["source_observations"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "Git blob/path"):
                self.check(x)

    def test_duplicate_or_unknown_claims_rejected(self):
        x = deepcopy(self.ledger)
        x["source_observations"][1] = deepcopy(x["source_observations"][0])
        with self.assertRaisesRegex(ValueError, "repeated"):
            self.check(x)
        x = deepcopy(self.ledger)
        x["source_observations"][0]["id"] = "POST_PR_GOLD_PATCH"
        with self.assertRaisesRegex(ValueError, "unknown"):
            self.check(x)

    def test_no_free_text_evidence_or_oracle_fields_in_observation(self):
        for field in ("claim_text", "prompt", "gold_patch", "expected_output"):
            x = deepcopy(self.ledger)
            x["source_observations"][0][field] = "post-fix"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "hidden leakage"):
                self.check(x)

    def test_evidence_grade_must_be_unexecuted(self):
        x = deepcopy(self.ledger)
        x["source_observations"][0]["evidence_level"] = "VALIDATED_SUCCESS"
        with self.assertRaisesRegex(ValueError, "cannot certify"):
            self.check(x)

    def test_shortened_or_extended_claim_catalogue_fails(self):
        for new in (self.ledger["source_observations"][:-1],
                    self.ledger["source_observations"] +
                    [deepcopy(self.ledger["source_observations"][-1])]):
            x = deepcopy(self.ledger)
            x["source_observations"] = new
            with self.assertRaisesRegex(ValueError, "exactly five"):
                self.check(x)

    def test_time_travel_parent_issue_rejected(self):
        for value in ("2026-10-22T22:55:40Z", "2026-10-24T00:00:00Z"):
            x = deepcopy(self.ledger)
            x["parent_issue_created_at"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "order invalid"):
                self.check(x)
        x = deepcopy(self.ledger)
        x["parent_issue_updated_at"] = "2026-10-20T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "update before"):
            self.check(x)

    def test_datetime_and_dates_must_be_observation_safe(self):
        for value in ("not-a-date", "2026-10-22T22:52:00", 5):
            x = deepcopy(self.ledger)
            x["parent_issue_created_at"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.check(x)
        x = deepcopy(self.ledger)
        x["observed_on"] = "2026-01-01"
        with self.assertRaisesRegex(ValueError, "after observation day"):
            self.check(x)

    def test_canonical_tree_identity_not_overridable(self):
        x = deepcopy(self.trees)
        x["records"][0]["observed_existing_source"][0]["git_blob_sha"] = "a"*40
        with self.assertRaisesRegex(ValueError, "differs from canonical tree"):
            self.check(trees=x)

    def test_canonical_issue_sha_not_overridable(self):
        x = deepcopy(self.chronology)
        x["records"][0]["pr_base_sha"] = "a"*40
        with self.assertRaisesRegex(ValueError, "immutable PR SHA"):
            self.check(chronology=x)


if __name__ == "__main__":
    unittest.main()
