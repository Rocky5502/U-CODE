"""Adversarial self-consistency tests for manuscript source, NOT a PDF compile."""
from pathlib import Path
import unittest

from scripts.audit_overleaf_sources import (
    MAIN, BIB, audit_manuscript, uncomment,
)


class SpringerOverleafSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paper = MAIN.read_text(encoding="utf-8")
        cls.bib = BIB.read_text(encoding="utf-8")

    def check(self, paper=None, bib=None):
        return audit_manuscript(
            self.paper if paper is None else paper,
            self.bib if bib is None else bib)

    def test_source_lint_handles_real_24_reference_paper(self):
        r = self.check()
        self.assertEqual(r["citations_used"], 24)
        self.assertEqual(r["undefined_crossreferences"], [])
        self.assertTrue(r["environment_delimiters_balanced"])
        self.assertEqual(r["keyword_count"], 6)
        self.assertFalse(r["real_rq_results_verified"])
        self.assertFalse(r["live_overleaf_modified"])

    def test_missing_bibliography_key_fails(self):
        with self.assertRaisesRegex(ValueError, "missing citations"):
            self.check(self.paper.replace(
                "\\cite{kulkarni2026pats}", "\\cite{unpublishedFake2026}", 1))

    def test_undefined_equation_reference_fails(self):
        with self.assertRaisesRegex(ValueError, "undefined LaTeX"):
            self.check(self.paper.replace(
                "\\eqref{eq:paired}", "\\eqref{eq:not-existing}", 1))

    def test_duplicate_label_fails(self):
        with self.assertRaisesRegex(ValueError, "duplicate LaTeX"):
            self.check(self.paper.replace(
                "\\label{sec:conclusions}", "\\label{sec:introduction}", 1))

    def test_malformed_environment_nesting_fails(self):
        with self.assertRaisesRegex(ValueError, "mismatched"):
            self.check(self.paper.replace(
                "\\end{tabular}", "\\end{align}", 1))

    def test_insufficient_abstract_words_fails(self):
        import re
        source = re.sub(r"(?s)\\abstract\{%.*?\n\}",
                        r"\\abstract{%\nThis is a short abstract.\n}",
                        self.paper, count=1)
        with self.assertRaisesRegex(ValueError, "150-250"):
            self.check(source)

    def test_manuscript_and_bib_both_required(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            self.check(bib="")

    def test_missing_publisher_class_fails(self):
        with self.assertRaisesRegex(ValueError, "Springer"):
            self.check(self.paper.replace(
                "\\documentclass[pdflatex,sn-basic]{sn-jnl}",
                "\\documentclass{article}", 1))

    def test_results_boundary_cannot_disappear(self):
        with self.assertRaisesRegex(ValueError, "prospective result boundary"):
            self.check(self.paper.replace(
                "NO EMPIRICAL RQ RESULTS EXIST", "OUR RESULTS WIN", 1))

    def test_duplicate_bib_entry_fails(self):
        fake = "\n@article{kulkarni2026pats, title={duplicate}}\n"
        with self.assertRaisesRegex(ValueError, "duplicate BibTeX"):
            self.check(bib=self.bib + fake)

    def test_comments_are_ignored_as_ref_occurrences(self):
        extra = self.paper + "\n% \\eqref{fake:fromcomment}\n"
        self.check(extra)

    def test_corrupted_premature_document_end_rejected(self):
        # Regression: an unsafe string replacement accidentally duplicated the
        # manuscript after an embedded end-of-document; never accept it again.
        broken=self.paper.replace(
            r"\section{Results}",
            r"\end{document}"+"\\n"+r"\section{Results}",1)
        self.assertNotEqual(broken, self.paper)
        with self.assertRaisesRegex(ValueError,"duplicate/premature"):
            self.check(broken)

    def test_trailing_noncomment_content_after_end_rejected(self):
        with self.assertRaisesRegex(ValueError,"trailing content"):
            self.check(self.paper+"\\n"+"UNAUTHORIZED SECOND MANUSCRIPT")

    def test_escape_percent_preserved_in_comment_strip(self):
        s = "valid 10\\% samples % private draft comment"
        self.assertIn("10\\% samples", uncomment(s))
        self.assertNotIn("private draft", uncomment(s))


if __name__ == "__main__":
    unittest.main()
