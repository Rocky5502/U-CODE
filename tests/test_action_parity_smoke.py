"""Synthetic action comparison and manuscript claims remain aligned."""
from pathlib import Path
import unittest

from examples.action_parity_smoke import reproduce_parity

ROOT=Path(__file__).resolve().parents[1]


class ActionParitySmokeTests(unittest.TestCase):
    def test_five_invented_tools_have_static_parity(self):
        result=reproduce_parity()
        self.assertEqual(result["action_count"],5)
        self.assertTrue(result["same_five_resource_budget"])
        self.assertEqual(len(result["opportunity_digest"]),64)
        self.assertEqual(result["real_model_runs"],0)
        self.assertIsNone(result["measured_effectiveness"])

    def test_parity_smoke_is_deterministic(self):
        self.assertEqual(reproduce_parity(),reproduce_parity())

    def test_manuscript_explicitly_limits_fixed_schedule_comparator(self):
        text=(ROOT/"paper/overleaf/main.tex").read_text(encoding="utf-8")
        self.assertIn(r"\label{eq:action-parity}",text)
        self.assertIn("fixed-schedule controller",text)
        self.assertIn("strongest",text)
        self.assertIn("does not establish a performance",text)


if __name__=="__main__":
    unittest.main()
