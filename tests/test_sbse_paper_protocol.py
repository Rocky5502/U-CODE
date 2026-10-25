"""Submission-context and preexperimental method integrity tests."""
from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class JournalSEMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tex = (ROOT/"paper/overleaf/main.tex").read_text(encoding="utf-8")
        cls.bib = (ROOT/"paper/overleaf/references.bib").read_text(encoding="utf-8")
        cls.plan = json.loads((ROOT/"configs/confirmatory_sbse_protocol_2026-10-25.json").read_text(encoding="utf-8"))

    def test_closest_verifier_prior_work_is_cited_not_claimed_original(self):
        for key in ("li2026retrace", "zeng2026dockerless",
                    "zheng2026sweproverified"):
            with self.subTest(key=key):
                self.assertIn(r"\cite{", self.tex)
                self.assertIn(key, self.tex)
                self.assertRegex(self.bib,
                                 r"@(misc|inproceedings)\{"+key+r",")

    def test_named_baseline_and_cost_contract_in_methods(self):
        for x in ("eight-policy matrix", "uncertainty-free search",
                  "Monte Carlo tree search", "trajectory replay",
                  "model revision", "tool entitlements",
                  "execution environment", "five-component",
                  r"\label{eq:receipt-integrity}"):
            with self.subTest(x=x):
                self.assertIn(x, self.tex)

    def test_paper_has_no_empirical_rq_results(self):
        self.assertIn("% NO EMPIRICAL RQ RESULTS EXIST", self.tex)
        self.assertIn("actual frozen", self.tex.lower())
        self.assertEqual(self.plan["qualified_task_ids"], [])
        self.assertFalse(self.plan["results_measured"])

    def test_six_checkpoints_aligned_with_study_protocol(self):
        self.assertEqual(len(self.plan["model_ids"]), 6)
        self.assertEqual(len(self.plan["policy_ids"]), 8)
        self.assertEqual(self.plan["primary_comparator"], "no_uncertainty_search")


if __name__=="__main__":
    unittest.main()
