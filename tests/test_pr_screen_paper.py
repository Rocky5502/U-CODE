"""Source-grounded, descriptive manuscript attrition checks only."""
from pathlib import Path
import unittest

from scripts.summarize_audit import load_manifest, load_records, summarize


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/overleaf/main.tex"
README = ROOT / "README.md"


class ProvenanceManuscriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m = load_manifest(ROOT / "data/discovery/agent_pr_candidates_120.csv")
        cls.stats = summarize(load_records(ROOT / "data/audits/2026-10-24", m), m)
        cls.paper = PAPER.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")

    def test_paper_table_matches_recomputed_metadata_class_counts(self):
        mapping = {
            "Production-source paths detected": "production_source_path_detected",
            "Test-only source changes": "test_only_source_change",
            "Non-source changes": "non_source_change",
            "Empty changed-file list; further review": "empty_file_list_needs_review",
            "Unretrievable PR link": "retrieval_failed",
        }
        for latex_label, code in mapping.items():
            expected = self.stats["source_status_counts"][code]
            with self.subTest(status=code):
                self.assertIn(f"{latex_label} & {expected}\\\\", self.paper)
        self.assertIn(r"\label{tab:pr-screen}", self.paper)

    def test_no_stale_pr_screen_counts_left_in_readme(self):
        self.assertIn("120/120 links attempted, 119/120 PRs retrieved",
                      self.readme)
        self.assertIn("zero fully eligible executable tasks", self.readme)
        self.assertNotIn("84/120 links attempted", self.readme)

    def test_metadata_table_does_not_claim_model_effect_or_code_execution(self):
        start = self.paper.index(r"\subsection{Completed PR-discovery metadata screen}")
        end = self.paper.index(r"\subsection{Evidence-qualified task admission}")
        section = self.paper[start:end]
        self.assertIn("No repository source was executed", section)
        self.assertIn("independently qualified experimental tasks", section)
        self.assertIn(r"\textbf{zero}", section)


if __name__ == "__main__":
    unittest.main()
