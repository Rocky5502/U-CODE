"""Two actual GitHub commit/patch inspections; no external source execution."""
import json
from pathlib import Path
import unittest

from scripts.summarize_audit import load_manifest


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data/audits/2026-10-25/deep_pr_manual_review_2.jsonl"


class RealManualEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [json.loads(x) for x in CASES.read_text(
            encoding="utf-8").splitlines() if x]
        cls.manifest = load_manifest(ROOT / "data/discovery/agent_pr_candidates_120.csv")

    def test_both_cases_from_original_frozen_search_manifest(self):
        self.assertEqual([r["candidate_id"] for r in cls_rows(self.rows)], [14, 49])
        for r in self.rows:
            original = self.manifest[r["candidate_id"]]
            self.assertEqual(r["pr_url"], original["agent_pr_url"])
            self.assertEqual(r["repository"], original["repository"])

    def test_commit_hashes_license_blobs_and_oracle_holds(self):
        for r in self.rows:
            for sha in [*r["commit_shas"], r["root_license_file_sha"]]:
                self.assertRegex(sha, "^[0-9a-f]{40}$")
            self.assertEqual(r["repository_license_spdx"], "Apache-2.0")
            self.assertEqual(r["file_specific_license_rights"], "PENDING")
            self.assertEqual(r["ai_generated_line_fraction"], "UNKNOWN")
            self.assertEqual(r["functional_independent_oracle"], "NOT_EXECUTED")
            self.assertFalse(r["dataset_eligible"])

    def test_text_matching_is_not_relabelled_executable_oracle(self):
        by_id = {x["candidate_id"]: x for x in self.rows}
        self.assertIn("text patterns", by_id[14]["observed_patch_semantics"])
        self.assertIn("adversarial_review", by_id[49]["security_flag"])
        self.assertIn("LOW_PRIORITY", by_id[14]["candidate_for_human_sandbox_feasibility"])


def cls_rows(rows):
    return sorted(rows, key=lambda r: r["candidate_id"])


if __name__ == "__main__":
    unittest.main()
