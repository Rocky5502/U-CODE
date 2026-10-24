"""First-party Springer draft checks, not a sn-jnl compilation."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "overleaf" / "main.tex"


class ConditionalPaperTests(unittest.TestCase):
    def test_history_conditional_posterior_equations_are_documented(self):
        content = PAPER.read_text(encoding="utf-8")
        self.assertIn(r"\label{sec:conditional}", content)
        self.assertIn(r"\label{eq:conditional-likelihood}", content)
        self.assertIn(r"\label{eq:conditional-bayes}", content)
        self.assertIn("redundant evidence", content)

    def test_method_discloses_no_trained_real_diagnostics(self):
        content = PAPER.read_text(encoding="utf-8")
        self.assertIn("no real fitted", content)
        self.assertIn("not measured success", content)
        self.assertIn("% NO EMPIRICAL RQ RESULTS EXIST", content)


if __name__ == "__main__":
    unittest.main()
