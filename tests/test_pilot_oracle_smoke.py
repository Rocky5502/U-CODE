"""Keep prospective evaluator demo from ever pretending real RQ results."""
from pathlib import Path
import unittest

from examples.pilot_oracle_boundary_smoke import demo


class PilotOracleSmokeTests(unittest.TestCase):
    def test_only_real_two_candidates_registered_and_none_approved(self):
        r = demo()
        self.assertEqual(r["registered_pilot_ids"], [43, 104])
        self.assertEqual(r["approved_pilots"], 0)
        self.assertIn("NO_EXTERNAL_CODE_EXECUTED", r["warning"])
        self.assertIn("NO_SEALED_ORACLE", r["warning"])

    def test_odd_pool_has_two_distinct_potential_allocations(self):
        r = demo()
        self.assertEqual(r["go_hypothetical_recovered_pool"], 5)
        self.assertEqual(
            {tuple(x) for x in r["go_multiple_fair_allocations"]},
            {(2,3), (3,2)},
        )

    def test_springer_methods_explicitly_contain_boundary_and_construction(self):
        s = Path("paper/overleaf/main.tex").read_text(encoding="utf-8")
        self.assertIn(r"\label{eq:oracle-ambiguity}", s)
        self.assertIn("evaluator-only", s)
        self.assertIn("no sealed oracle", s)
        self.assertIn("not a correctness finding", s)


if __name__ == "__main__":
    unittest.main()
