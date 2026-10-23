import unittest

from ucode.acquisition import (
    ParetoPoint, AcquisitionProposal, hypervolume_2d,
    expected_hvi_per_cost, select_ehvi_action,
)


class AcquisitionTests(unittest.TestCase):
    def test_empty_archive(self):
        self.assertEqual(hypervolume_2d([]), 0)

    def test_single_point(self):
        self.assertAlmostEqual(hypervolume_2d([ParetoPoint(.5, .6)]), .3)

    def test_two_nondominated_points(self):
        ps = [ParetoPoint(.5, .9), ParetoPoint(.9, .5)]
        self.assertAlmostEqual(hypervolume_2d(ps), .65)
        self.assertAlmostEqual(hypervolume_2d(ps + [ParetoPoint(.1, .1)]), .65)

    def test_reference(self):
        self.assertAlmostEqual(
            hypervolume_2d([ParetoPoint(.8, .7)], ParetoPoint(.2, .3)), .24)

    def test_invalid_objectives(self):
        with self.assertRaises(ValueError):
            ParetoPoint(1.2, .3)

    def test_ehvi_exact_when_sd_zero(self):
        p = AcquisitionProposal("generate", .8, 0, .5, 0, 1, 2)
        self.assertAlmostEqual(expected_hvi_per_cost([], p, 8), .2)

    def test_ehvi_zero_probability(self):
        p = AcquisitionProposal("test", .8, 0, .5, 0, 0, 1)
        self.assertEqual(expected_hvi_per_cost([], p, 8), 0)

    def test_selection_budget(self):
        expensive = AcquisitionProposal("generate", .8, 0, .9, 0, 1, 10)
        cheap = AcquisitionProposal("test", .6, 0, .5, 0, 1, 1)
        self.assertEqual(select_ehvi_action([], [expensive, cheap], 2, 8), cheap)
        self.assertIsNone(select_ehvi_action([], [expensive], 2, 8))

    def test_reliability_gate(self):
        p = AcquisitionProposal("repair", .3, .1, .2, .1, 1, 1)
        self.assertIsNone(select_ehvi_action([], [p], 2, 10,
                            minimum_mean_reliability=.8))

    def test_seed_reproducible(self):
        p = AcquisitionProposal("generate", .5, .2, .4, .1, .9, 1)
        self.assertEqual(expected_hvi_per_cost([], p, 23, 7),
                         expected_hvi_per_cost([], p, 23, 7))


if __name__ == "__main__":
    unittest.main()
