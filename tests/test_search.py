import unittest

from ucode.search import (
    ActionEstimate, SearchState, choose_action, dominates, pareto_frontier,
)
from ucode.simulation import run_synthetic_episode


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.actions = [
            ActionEstimate("generate", .25, .1, .1, 3),
            ActionEstimate("test", .01, .8, .05, 1),
            ActionEstimate("repair", .4, .01, .1, 3),
            ActionEstimate("static_analysis", .02, .3, .6, 2),
        ]

    def test_frontier_drops_dominated(self):
        high = ActionEstimate("test", .3, .4, .4, 1)
        low = ActionEstimate("generate", .1, .1, .1, 2)
        self.assertTrue(dominates(high, low))
        self.assertEqual(pareto_frontier([high, low]), [high])

    def test_no_dominance_for_tradeoff(self):
        a = ActionEstimate("test", 0, 1, 0, 1)
        b = ActionEstimate("repair", 1, 0, 0, 1)
        self.assertEqual(len(pareto_frontier([a, b])), 2)

    def test_budget_is_hard_constraint_all_policies(self):
        for p in ("uncertainty_pareto", "random", "cost_first",
                  "fixed_test", "quality_only"):
            state = SearchState(.8, .75)
            result = choose_action(state, self.actions, p)
            self.assertEqual(result.action, "abstain")

    def test_no_candidate_cannot_test_or_repair(self):
        state = SearchState(3, .4, has_candidate=False)
        out = choose_action(state, self.actions, "uncertainty_pareto")
        self.assertEqual(out.action, "generate")

    def test_fixed_test(self):
        self.assertEqual(choose_action(SearchState(5, .5),
                                       self.actions, "fixed_test").action, "test")

    def test_random_reproducible(self):
        state = SearchState(5, .5)
        self.assertEqual(choose_action(state, self.actions, "random", 9),
                         choose_action(state, self.actions, "random", 9))

    def test_bad_action(self):
        with self.assertRaises(ValueError):
            ActionEstimate("upload_secrets", 1, 1, 1, 1)
        with self.assertRaises(ValueError):
            ActionEstimate("test", -1, 1, 1, 1)
        with self.assertRaises(ValueError):
            choose_action(SearchState(1, .5), [], "unknown")

    def test_synthetic_episode_is_labeled(self):
        a = run_synthetic_episode("uncertainty_pareto", 7)
        b = run_synthetic_episode("uncertainty_pareto", 7)
        self.assertEqual(a, b)
        self.assertTrue(a.synthetic_only)
        self.assertLessEqual(a.budget_spent, 9)


if __name__ == "__main__":
    unittest.main()
