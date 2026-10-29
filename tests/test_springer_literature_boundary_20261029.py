"""Protect the two source-verified, published related-work additions."""
from pathlib import Path
import unittest
from scripts.audit_overleaf_sources import audit_manuscript

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper/overleaf/main.tex"
BIB = ROOT / "paper/overleaf/references.bib"

class SpringerLiteratureBoundaryTests(unittest.TestCase):
    def test_both_primary_literature_sources_and_citations(self):
        tex = TEX.read_text(encoding="utf-8")
        bib = BIB.read_text(encoding="utf-8")
        for key in ("zainullina2025guided", "dakhama2025searchsys"):
            with self.subTest(key=key):
                self.assertIn("\\cite{" + key + "}", tex)
                self.assertIn("{" + key + ",", bib)
        result = audit_manuscript(tex, bib)
        self.assertEqual(result["undefined_citations"], [])
        self.assertEqual(result["novelty_comparison"]["real_ucode_results"], 0)

    def test_no_claim_of_real_head_to_head_comparison(self):
        tex = TEX.read_text(encoding="utf-8")
        self.assertIn("No head-to-head comparison has yet been performed.", tex)
        self.assertIn("We will not use its defect counts as U-CODE outcomes.", tex)
        self.assertIn("No reliability improvement", tex)

if __name__ == "__main__":
    unittest.main()
