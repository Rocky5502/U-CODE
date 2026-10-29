"""Equation inventory is exhaustive by source label, not a claim of 33 proofs."""
import unittest
from scripts.audit_manuscript_equations import (
    PAPER, EXPECTED_FROZEN_LABELS, LIMITED_CROSSCHECKS, audit_equations,
)

class EquationRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tex=PAPER.read_text(encoding="utf-8")

    def test_all_33_paper_equations_have_explicit_review_status(self):
        data=audit_equations(self.tex)
        self.assertEqual(data["total_equations"],33)
        self.assertEqual(data["limited_synthetic_crosschecks"],7)
        self.assertEqual(data["pending_independent_derivation"],26)
        self.assertEqual(data["full_theorem_reviews_completed"],0)
        self.assertEqual(data["real_model_evaluations"],0)
        self.assertEqual(
            {r["equation_id"] for r in data["equations"]},EXPECTED_FROZEN_LABELS)
        self.assertTrue(all(
            r["external_human_reviewed"] is False and
            r["empirically_validated"] is False and
            r["statistical_guarantee_established"] is False
            for r in data["equations"]))

    def test_missing_mathematical_equation_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"register drift"):
            audit_equations(self.tex.replace(
                r"\label{eq:bes}",r"\label{eq:deleted-bes}",1))

    def test_duplicate_mathematical_equation_fails(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            audit_equations(self.tex.replace(
                r"\label{eq:bes}",r"\label{eq:evsi}",1))

    def test_seven_limited_checks_never_promoted_to_theorem_proofs(self):
        data=audit_equations(self.tex)
        for r in data["equations"]:
            if r["equation_id"] in LIMITED_CROSSCHECKS:
                self.assertEqual(r["stage"],"LIMITED_SYNTHETIC_CROSSCHECK")
            else:
                self.assertEqual(r["stage"],"PENDING_DERIVATION_REVIEW")

if __name__=="__main__":
    unittest.main()
