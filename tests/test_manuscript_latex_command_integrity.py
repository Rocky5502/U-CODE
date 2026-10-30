"""Fail closed on doubled LaTeX command escapes in the U-CODE manuscript."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper" / "overleaf" / "main.tex"


class ManuscriptLatexCommandIntegrity(unittest.TestCase):
    def test_no_double_backslash_for_textual_latex_commands(self):
        text = MANUSCRIPT.read_text(encoding="utf-8")
        for command in ("cite", "emph", "section", "subsection", "paragraph",
                        "ref", "eqref", "label", "begin", "end", "textbf"):
            with self.subTest(command=command):
                self.assertNotIn("\\\\" + command + "{", text)

    def test_mathematical_and_results_disclaimers_present(self):
        text = MANUSCRIPT.read_text(encoding="utf-8")
        self.assertIn("NO EMPIRICAL RQ RESULTS EXIST", text)
        self.assertIn("partial-identification", text)
        self.assertIn("independent", text.lower())


if __name__ == "__main__":
    unittest.main()
