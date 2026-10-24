"""Integrity linkage: real PR dossiers vs prospective Springer methods."""
from pathlib import Path
import json
import unittest

from ucode.task_admission import REQUIRED_GATES

ROOT = Path(__file__).resolve().parents[1]


class AdmissionPaperIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tex = (ROOT / "paper/overleaf/main.tex").read_text(encoding="utf-8")
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.records = [json.loads(line) for line in (
            ROOT / "data/admission/2026-10-25/pilot_dossiers.jsonl"
        ).read_text(encoding="utf-8").splitlines() if line]

    def test_manuscript_names_both_actual_prs_without_claiming_execution(self):
        for fragment in ("mvdbos/php-spider", "PlayHuai/eighty-point-huai-an",
                         "eight open gates each", "Neither candidate has been",
                         "external independent"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.tex)

    def test_readme_does_not_pretend_pilot_task_is_approved(self):
        self.assertIn("16/16 gates currently PENDING", self.readme)
        self.assertIn("neither candidate is an admitted", self.readme)

    def test_dossiers_have_real_sha_anchors_and_no_verified_gate(self):
        self.assertEqual({r["candidate_id"] for r in self.records}, {43, 104})
        self.assertEqual(sum(len(r["gates"]) for r in self.records), 16)
        for r in self.records:
            self.assertEqual({g["gate"] for g in r["gates"]},
                             set(REQUIRED_GATES))
            self.assertTrue(all(g["status"] == "PENDING" for g in r["gates"]))
            self.assertFalse(r.get("dataset_eligible", False))


if __name__ == "__main__":
    unittest.main()
