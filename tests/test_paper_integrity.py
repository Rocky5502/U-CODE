"""Offline structure checks; these do NOT replace compiling official sn-jnl."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "overleaf"


class PaperIntegrityTests(unittest.TestCase):
    def test_springer_class_and_bib_file(self):
        main = (PAPER / "main.tex").read_text(encoding="utf-8")
        self.assertIn(r"\documentclass[pdflatex,sn-basic]{sn-jnl}", main)
        self.assertIn(r"\bibliography{references}", main)
        self.assertTrue((PAPER / "references.bib").exists())

    def test_every_paper_citation_matches_a_real_bib_key(self):
        main = (PAPER / "main.tex").read_text(encoding="utf-8")
        bib = (PAPER / "references.bib").read_text(encoding="utf-8")
        entries = re.findall(r"@\w+\{\s*([^,\s]+)\s*,", bib)
        self.assertEqual(len(entries), len(set(entries)))
        self.assertGreaterEqual(len(entries), 16)
        self.assertIn("mohsin2026teachingagents", entries)
        self.assertIn("hu2026swecritix", entries)
        cites = re.findall(r"\cite(?:\[[^]]*\])?\{([^}]+)\}", main)
        used = {key.strip() for group in cites for key in group.split(",")}
        self.assertTrue(used)
        self.assertFalse(used - set(entries), sorted(used - set(entries)))

    def test_bes_method_references_its_equations_and_conservative_scope(self):
        main = (PAPER / "main.tex").read_text(encoding="utf-8")
        self.assertIn(r"\subsection{Bounded Evidence Search}", main)
        self.assertIn(r"\label{eq:bes}", main)
        self.assertIn(r"\label{eq:beszero}", main)
        self.assertIn("single active patch", main)
        self.assertIn("hypothetical", main)
        self.assertIn("conditionally independent", main)

    def test_prospective_abstract_and_no_fabricated_rq_results(self):
        main = (PAPER / "main.tex").read_text(encoding="utf-8")
        m = re.search(r"\abstract\{%\s*(.*?)\s*\}\s*\\keywords", main, re.S)
        self.assertIsNotNone(m)
        # Strip comment-only lines before counting actual abstract words.
        abstract = re.sub(r"(?m)^\s*%.*$", "", m.group(1))
        self.assertGreaterEqual(len(abstract.split()), 150)
        self.assertLessEqual(len(abstract.split()), 250)
        self.assertIn("% NO EMPIRICAL RQ RESULTS EXIST", main)
        self.assertIn(r"\section{Results}", main)


if __name__ == "__main__":
    unittest.main()
