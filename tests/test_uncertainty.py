import math
import unittest

from ucode.uncertainty import (
    binary_entropy, predictive_entropy, variation_ratio,
    brier_score, expected_calibration_error, risk_coverage_curve,
)


class UncertaintyTests(unittest.TestCase):
    def test_entropy_boundaries(self):
        self.assertEqual(binary_entropy(0), 0)
        self.assertEqual(binary_entropy(1), 0)
        self.assertAlmostEqual(binary_entropy(.5), 1)

    def test_binary_entropy_symmetry(self):
        self.assertAlmostEqual(binary_entropy(.2), binary_entropy(.8))

    def test_invalid_probability(self):
        for x in (-.1, 1.1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                binary_entropy(x)

    def test_multiclass_entropy(self):
        self.assertAlmostEqual(predictive_entropy([.25] * 4), 1)
        self.assertEqual(predictive_entropy([1, 0, 0]), 0)
        with self.assertRaises(ValueError):
            predictive_entropy([.5, .3])

    def test_disagreement(self):
        self.assertEqual(variation_ratio(["x", "x", "x"]), 0)
        self.assertAlmostEqual(variation_ratio(["x", "y", "x", "y"]), .5)
        with self.assertRaises(ValueError):
            variation_ratio([])

    def test_brier_perfect_and_bad(self):
        self.assertEqual(brier_score([0, 1], [0, 1]), 0)
        self.assertEqual(brier_score([1, 0], [0, 1]), 1)

    def test_ece_perfect(self):
        self.assertEqual(expected_calibration_error([0, 1], [0, 1]), 0)

    def test_ece_nontrivial(self):
        self.assertAlmostEqual(expected_calibration_error([.9, .9], [1, 0]), .4)

    def test_invalid_labels_and_lengths(self):
        with self.assertRaises(ValueError):
            brier_score([.5], [2])
        with self.assertRaises(ValueError):
            brier_score([.5], [])
        with self.assertRaises(ValueError):
            brier_score([.5], [True])
        with self.assertRaises(ValueError):
            expected_calibration_error([.5], [1], bins=0)

    def test_risk_coverage_sorted(self):
        self.assertEqual(risk_coverage_curve([.1, .9], [0, 1]),
                         [(.5, 0), (1., .5)])


if __name__ == "__main__":
    unittest.main()
