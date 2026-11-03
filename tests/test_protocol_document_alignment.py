"""Keep human-readable prospective protocol aligned with the frozen study manifest.

These are source-integrity checks only. They do not execute LLMs, external code,
independent oracles, or any confirmed software-repair study.
"""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "RESEARCH_PROTOCOL.md"
CONTRACT = ROOT / "configs" / "confirmatory_sbse_protocol_2026-10-25.json"
MODELS = ROOT / "configs" / "accepted_six_model_study_2026-10-25.json"
STATUS = ROOT / "docs" / "UCODE_RESEARCH_PROGRESS_2026-11-03.md"


class HumanProtocolRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.models = json.loads(MODELS.read_text(encoding="utf-8"))
        cls.status = STATUS.read_text(encoding="utf-8")

    def test_model_roster_matches_canonical_manifest(self):
        selected = [m["model_id"] for m in self.models["models"]]
        self.assertEqual(self.contract["model_ids"], selected)
        self.assertEqual(len(selected), 6)
        for model_id in selected:
            with self.subTest(model=model_id):
                self.assertIn("`" + model_id + "`", self.text)
        self.assertNotIn("| Models | Qwen2.5-Coder-7B, Qwen3-8B", self.text)

    def test_eight_policy_ids_are_explicit_and_primary_contrast_frozen(self):
        self.assertEqual(len(self.contract["policy_ids"]), 8)
        for policy_id in self.contract["policy_ids"]:
            with self.subTest(policy=policy_id):
                self.assertIn("`" + policy_id + "`", self.text)
        self.assertEqual(self.contract["primary_treatment"], "ucode_conditional_bes")
        self.assertEqual(self.contract["primary_comparator"], "no_uncertainty_search")
        self.assertIn("intention-to-treat", self.text)
        self.assertNotIn("| Agent policies | no-search, random", self.text)

    def test_empirical_admission_remains_blocked(self):
        self.assertEqual(self.contract["qualified_task_ids"], [])
        self.assertFalse(self.contract["results_measured"])
        self.assertFalse(self.contract["model_revisions_frozen"])
        self.assertFalse(self.contract["independent_oracles_sealed"])
        self.assertFalse(self.contract["runner_isolated_and_attested"])
        self.assertIn("zero", self.text.lower())
        for phrase in ("0/6", "0/8", "0 admitted tasks", "0 sealed oracles"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.status)

    def test_five_resource_names_and_current_scientific_milestones(self):
        for name in ("tokens", "test_calls", "gpu_seconds",
                     "cpu_seconds", "wall_seconds"):
            with self.subTest(resource=name):
                self.assertIn(name, self.text)
        for milestone in ("M1", "M2", "M3", "M4", "M5", "M6", "G5"):
            with self.subTest(milestone=milestone):
                self.assertIn("**" + milestone + " / issue #", self.text)


if __name__ == "__main__":
    unittest.main()
