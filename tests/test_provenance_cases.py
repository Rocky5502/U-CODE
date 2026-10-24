"""Offline consistency checks for the two observed PR commit history snapshots.

These protect original metadata/denominators, not prove actual AI line ownership.
"""
import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data/audits/2026-10-24/two_pr_commit_and_license_deep_check.jsonl"
DISCOVERY = ROOT / "data/discovery/agent_pr_candidates_120.csv"


class HumanAgentCommitProvenanceCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = [json.loads(line) for line in CASES.read_text().splitlines()]
        with DISCOVERY.open(newline="", encoding="utf-8") as f:
            cls.discovery = list(csv.DictReader(f))

    def test_cases_are_actual_discovered_candidate_links(self):
        originals = {row["agent_pr_url"] for row in self.discovery}
        self.assertEqual(len(self.cases), 2)
        for row in self.cases:
            self.assertIn(row["pr_url"], originals)

    def test_immutable_base_head_merge_and_commits(self):
        for row in self.cases:
            for key in ("base_sha", "head_sha", "merge_sha"):
                self.assertRegex(row[key], "^[0-9a-f]{40}$")
            self.assertEqual(row["head_sha"], row["commits"][-1]["sha"])
            self.assertEqual(len(row["commits"]), 3)
            self.assertRegex(row["root_license_blob_sha"], "^[0-9a-f]{40}$")

    def test_commit_provenance_patterns_are_distinct(self):
        by_repo = {row["repository"]: row for row in self.cases}
        dep = by_repo["dependabot/dependabot-core"]
        self.assertTrue(all(c["github_author"] != "Copilot" for c in dep["commits"]))
        self.assertTrue(all(c["copilot_coauthor_trailer"] for c in dep["commits"]))
        cpp = by_repo["xadupre/onnx-light-cpu"]
        self.assertTrue(all(c["github_author"] == "Copilot" for c in cpp["commits"]))
        self.assertEqual(sum(c.get("human_coauthor_trailer", False)
                             for c in cpp["commits"]), 2)

    def test_neither_case_promoted_without_independent_oracle(self):
        for row in self.cases:
            self.assertFalse(row["qualified_for_study"])
            self.assertEqual(row["ai_line_attribution"], "UNVERIFIED")
            self.assertEqual(row["file_level_rights"], "PENDING")
            self.assertEqual(row["independent_functional_oracle"], "NOT_EXECUTED")


if __name__ == "__main__":
    unittest.main()
