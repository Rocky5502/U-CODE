"""Verify the published camera-ready README SVG has correct directed edges."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_framework_figure import FIGURE, validate_framework_svg


class FigureFlowTests(unittest.TestCase):
    def test_published_figure_has_all_directed_edges(self):
        self.assertEqual(validate_framework_svg(), {
            "policy_edges": 5, "evaluation_edges": 3,
            "feedback_edges": 1, "cross_lane_edges": 2,
        })

    def test_reversed_policy_arrow_is_rejected(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "bad.svg"
            p.write_text(FIGURE.read_text(encoding="utf-8").replace(
                'd="M269 320 H278"', 'd="M278 320 H269"'),
                encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "reversed|misplaced"):
                validate_framework_svg(p)

    def test_missing_feedback_cannot_pass_camera_ready_check(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "bad.svg"
            p.write_text(FIGURE.read_text(encoding="utf-8").replace(
                'id="execution-to-BES-feedback"', 'id="wrong-direction"'),
                encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required"):
                validate_framework_svg(p)

    def test_releases_come_to_sealed_evaluator_not_training_model(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "bad.svg"
            p.write_text(FIGURE.read_text(encoding="utf-8").replace(
                'M1446 514 V601 H603 V683',
                'M1446 514 V601 H933 V683'), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "terminal patch"):
                validate_framework_svg(p)

    def test_no_embedded_script_or_external_image(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "bad.svg"
            p.write_text(FIGURE.read_text(encoding="utf-8").replace(
                "</svg>", "<script>alert('x')</script></svg>"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "scripts"):
                validate_framework_svg(p)


if __name__ == "__main__":
    unittest.main()
