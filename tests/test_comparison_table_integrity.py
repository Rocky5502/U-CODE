"""Evidence/status constraints on the cited Springer comparison, offline only."""
import unittest
from scripts.audit_overleaf_sources import (
    MAIN, BIB, audit_comparison_table, audit_manuscript,
)


class NoveltyTableIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paper = MAIN.read_text(encoding="utf-8")
        cls.bib = BIB.read_text(encoding="utf-8")

    def check(self, text=None):
        return audit_manuscript(self.paper if text is None else text, self.bib)

    def test_all_seven_original_related_sources_and_no_empirical_ucode(self):
        row = self.check()["novelty_comparison"]
        self.assertEqual(row["sources"], 7)
        self.assertEqual(row["real_ucode_results"], 0)
        self.assertEqual(row["interpretation"],
                         "DESCRIPTIVE_METHOD_POSITIONING_ONLY")

    def test_uses_symbols_without_implying_measured_superiority(self):
        src=self.paper
        self.assertIn(r"\newcommand{\methodYes}",src)
        self.assertIn(r"\newcommand{\methodNo}",src)
        self.assertIn(r"\newcommand{\methodPlan}",src)
        self.assertIn("not a performance",src)
        self.assertIn("not experimentally validated superiority",src)
        self.assertIn("not been conducted",src)

    def test_prevent_invented_ucode_success_tick(self):
        marker = r"\methodPlan & \methodNo"
        self.assertIn(marker,self.paper)
        changed = self.paper.replace(marker,r"\methodPlan & \methodYes",1)
        with self.assertRaisesRegex(ValueError,"real results absent"):
            self.check(changed)

    def test_prevent_unearned_method_tick_in_final_row(self):
        marker = r"\methodPlan & \methodNo"
        text = self.paper.replace(
            r"\textbf{U-CODE (this study; prospective)}",
            r"\textbf{U-CODE (this study; prospective)}",1)
        # Change first prospective marker inside the row, not a prior row.
        tail = text.index(r"\textbf{U-CODE (this study; prospective)}")
        before, after = text[:tail],text[tail:]
        after=after.replace(r"\methodPlan",r"\methodYes",1)
        with self.assertRaisesRegex(ValueError,"planned"):
            self.check(before+after)

    def test_missing_original_citation_fails(self):
        text=self.paper.replace(
            r"SWE-Replay (2026)~\cite{ding2026swereplay}",
            r"SWE-Replay (2026)",1)
        with self.assertRaisesRegex(ValueError,"primary-source"):
            self.check(text)

    def test_no_performance_promotion_in_table(self):
        text=self.paper.replace(
            "This is \\emph{not} a performance",
            "U-CODE outperforms all baselines. This is \\emph{not} a performance",
            1)
        # Depending on whether prose was inserted inside the caption,
        # the audit must either catch the promotion or lack of an exact caveat.
        with self.assertRaises(ValueError):
            self.check(text)

    def test_removed_table_fails(self):
        text=self.paper.replace(r"\begin{table*}[t]",r"\begin{figure*}[t]",1)
        with self.assertRaisesRegex(ValueError,"novelty comparison table"):
            self.check(text)

    def test_all_bib_references_already_resolve(self):
        out=self.check()
        self.assertEqual(out["undefined_citations"],[])
        self.assertEqual(out["undefined_crossreferences"],[])


if __name__ == "__main__":
    unittest.main()
