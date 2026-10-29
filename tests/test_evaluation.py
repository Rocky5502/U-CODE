"""Pure synthetic evaluator examples; no measured U-CODE effectiveness."""
import unittest
from dataclasses import replace

from ucode.evaluation import (
    EvaluationOutcome, measure_policy, paired_verified_success,
)


def outcome(task, group, policy, released, passed, model="model-a",
            seed=0, budget="pilot"):
    return EvaluationOutcome(task, group, model, seed, budget, policy,
                             released, passed)


class SealedEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.a = [
            outcome("t1", "A", "ucode", True, True),
            outcome("t2", "A", "ucode", False, None),
            outcome("t3", "B", "ucode", True, False),
            outcome("t4", "C", "ucode", True, True),
        ]
        self.b = [
            outcome("t1", "A", "fixed", True, False),
            outcome("t2", "A", "fixed", False, None),
            outcome("t3", "B", "fixed", True, True),
            outcome("t4", "C", "fixed", False, None),
        ]

    def test_policy_metrics_are_separate_from_abstention(self):
        m = measure_policy(self.a)
        self.assertEqual((m.attempts, m.successes, m.releases,
                          m.erroneous_releases), (4, 2, 3, 1))
        self.assertAlmostEqual(m.full_task_success, .5)
        self.assertAlmostEqual(m.coverage, .75)
        self.assertAlmostEqual(m.wrong_release_risk, 1 / 3)

    def test_always_abstain_is_zero_success_not_perfect_reliability(self):
        data = [outcome("t1", "A", "reject", False, None)]
        m = measure_policy(data)
        self.assertEqual(m.full_task_success, 0)
        self.assertEqual(m.coverage, 0)
        self.assertIsNone(m.wrong_release_risk)

    def test_no_pseudolabel_on_abstained_task(self):
        with self.assertRaises(ValueError):
            outcome("t1", "A", "p", False, False)
        with self.assertRaises(ValueError):
            outcome("t1", "A", "p", False, True)

    def test_released_requires_independent_bool_label(self):
        for label in (None, 1, 0, "pass"):
            with self.subTest(label=label), self.assertRaises(ValueError):
                outcome("t1", "A", "p", True, label)

    def test_paired_positive_negative_discordance(self):
        p = paired_verified_success(self.a + self.b, "ucode", "fixed",
                                    bootstrap_samples=0)
        self.assertEqual(p.pairs, 4)
        self.assertEqual(p.lineage_groups, 3)
        self.assertEqual(p.positive_discordant, 2)
        self.assertEqual(p.negative_discordant, 1)
        self.assertAlmostEqual(p.effect_success_difference, .25)
        self.assertIsNone(p.cluster_bootstrap_ci_95)

    def test_cluster_bootstrap_reproducible(self):
        x = paired_verified_success(self.a + self.b, "ucode", "fixed",
                                    bootstrap_samples=100, seed=42)
        y = paired_verified_success(list(reversed(self.b + self.a)),
                                    "ucode", "fixed",
                                    bootstrap_samples=100, seed=42)
        self.assertEqual(x, y)
        low, high = x.cluster_bootstrap_ci_95
        self.assertTrue(-1 <= low <= high <= 1)

    def test_seeds_are_repeated_within_same_task_lineage(self):
        extra = [replace(o, seed=1) for o in self.a + self.b]
        p = paired_verified_success(self.a + self.b + extra, "ucode", "fixed",
                                    bootstrap_samples=50, seed=3)
        self.assertEqual(p.pairs, 8)
        self.assertEqual(p.lineage_groups, 3)

    def test_reject_unmatched(self):
        with self.assertRaisesRegex(ValueError, "unmatched"):
            paired_verified_success(self.a + self.b[:-1], "ucode", "fixed", 0)

    def test_reject_mismatched_fork_group(self):
        corrupted = [replace(self.b[0], lineage_group="wrong")]
        with self.assertRaisesRegex(ValueError, "different fork"):
            paired_verified_success(self.a + corrupted + self.b[1:],
                                    "ucode", "fixed", 0)

    def test_reject_duplicate_evaluator_rows(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            measure_policy(self.a + [self.a[0]])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            paired_verified_success(self.a + self.b + [self.b[1]],
                                    "ucode", "fixed", 0)

    def test_reject_extra_policy_and_mixed_single_arm(self):
        with self.assertRaises(ValueError):
            measure_policy(self.a + self.b)
        with self.assertRaisesRegex(ValueError, "only two"):
            paired_verified_success(self.a + self.b
                                    + [outcome("t5", "D", "third", True, True)],
                                    "ucode", "fixed", 0)

    def test_empty_and_invalid_controls(self):
        with self.assertRaises(ValueError):
            measure_policy([])
        with self.assertRaises(ValueError):
            paired_verified_success([], "ucode", "fixed")
        with self.assertRaises(ValueError):
            paired_verified_success(self.a, "ucode", "ucode")
        with self.assertRaises(ValueError):
            paired_verified_success(self.a, "ucode", "fixed", -1)

    def test_same_task_cannot_switch_fork_lineage_across_seeds(self):
        # Within each matched seed the two policies agree, but task t1
        # is incorrectly relabeled as a NEW independent repository for seed 1.
        # Previously this silently inflated bootstrap cluster count.
        extra = [
            replace(o, seed=1, lineage_group="fake-independent-fork")
            if o.task_id == "t1" else replace(o, seed=1)
            for o in self.a + self.b
        ]
        with self.assertRaisesRegex(ValueError, "inconsistent fork lineage"):
            paired_verified_success(self.a + self.b + extra,
                                    "ucode", "fixed", bootstrap_samples=100)
        with self.assertRaisesRegex(ValueError, "inconsistent fork lineage"):
            measure_policy(self.a + [extra[0]])

    def test_same_task_cannot_change_lineage_across_models_or_budgets(self):
        for alteration in ({"model_id": "model-b"},
                           {"budget_id": "extended"}):
            a = [replace(o, lineage_group="fake-fork", **alteration)
                 for o in self.a if o.task_id == "t1"]
            b = [replace(o, lineage_group="fake-fork", **alteration)
                 for o in self.b if o.task_id == "t1"]
            with self.subTest(alteration=alteration), self.assertRaisesRegex(
                    ValueError, "inconsistent fork lineage"):
                paired_verified_success(self.a + self.b + a + b,
                                        "ucode", "fixed", bootstrap_samples=20)

    def test_boolean_bootstrap_count_is_not_a_valid_sample_size(self):
        with self.assertRaisesRegex(ValueError, "bootstrap_samples"):
            paired_verified_success(self.a + self.b, "ucode", "fixed",
                                    bootstrap_samples=True)

    def test_small_one_group_has_no_cluster_ci(self):
        a = [outcome("t1", "A", "u", True, True)]
        b = [outcome("t1", "A", "f", True, False)]
        p = paired_verified_success(a + b, "u", "f", bootstrap_samples=20)
        self.assertEqual(p.effect_success_difference, 1)
        self.assertIsNone(p.cluster_bootstrap_ci_95)

    def test_exact_same_outcomes_give_zero_effect_and_ci(self):
        a = [outcome("t1", "A", "u", True, True),
             outcome("t2", "B", "u", False, None)]
        b = [outcome("t1", "A", "f", True, True),
             outcome("t2", "B", "f", False, None)]
        m = paired_verified_success(a + b, "u", "f", bootstrap_samples=20)
        self.assertEqual(m.effect_success_difference, 0)
        self.assertEqual(m.cluster_bootstrap_ci_95, (0, 0))


if __name__ == "__main__":
    unittest.main()
