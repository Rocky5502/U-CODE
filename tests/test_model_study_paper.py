"""Guard researcher-selected six-model methods and README figure metadata."""
from pathlib import Path
import unittest

from ucode.model_readiness import load_selected_models

ROOT = Path(__file__).resolve().parents[1]


class SixModelPublicationTests(unittest.TestCase):
    def test_readme_includes_scalable_figure_and_plain_limits(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("![U-CODE framework:", readme)
        self.assertIn("docs/figures/ucode-framework.svg", readme)
        self.assertIn("Architectural design, not a completed", readme)

    def test_paper_lists_every_selected_model_without_pretending_runs(self):
        text = (ROOT / "paper/overleaf/main.tex").read_text(encoding="utf-8")
        for fragment in (
            "Qwen2.5-Coder-7B-Instruct",
            "Qwen3-Coder-30B-A3B-Instruct",
            "Devstral-Small-2-24B-Instruct-2512",
            "DeepSeek-Coder-V2-Lite-Instruct",
            "CodeGemma-1.1-7b-it",
            "Llama-3.1-8B-Instruct",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)
        self.assertIn("none", text.lower())
        self.assertIn("frozen", text.lower())

    def test_selection_does_not_falsely_indicate_license_acceptance_or_runs(self):
        selected = load_selected_models()
        self.assertEqual(len(selected["models"]), 6)
        self.assertTrue(all(m["selection"] == "user_selected_for_planning"
                            and m["study_included"] for m in selected["models"]))
        self.assertTrue(all(m["full_license_review"] == "PENDING"
                            and not m["model_weights_verified"]
                            and m["independently_verified_task_runs"] == 0
                            for m in selected["models"]))


if __name__ == "__main__":
    unittest.main()
