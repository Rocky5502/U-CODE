"""Leakage-resistant fitting tests using authored, entirely synthetic metadata.

No third-party code and no actual oracle predictions are executed here.
"""
import unittest

from ucode.diagnostic_fit import (
    DiagnosticTrainingRecord, FrozenDiagnosticLikelihood,
    GroupPartitions, fit_diagnostic_likelihood,
)
from ucode.vector_policy import (
    ResourceVector, ResourcePrices, choose_next_intervention,
)
from ucode.voi import ReleaseRule


def record(i, group, good, observed, model="pinned-model", action="test",
           evidence_time=100, oracle_time=200):
    return DiagnosticTrainingRecord(
        task_id=f"task-{i}", lineage_group=group, model_id=model,
        action=action, positive_evidence=observed,
        oracle_acceptable=good, evidence_time=evidence_time,
        oracle_time=oracle_time, oracle_id=f"sealed-{i}",
    )


class TrainOnlyDiagnosticFitting(unittest.TestCase):
    def setUp(self):
        self.groups = GroupPartitions(
            frozenset({"repo-A", "repo-B"}),
            frozenset({"repo-C"}), frozenset({"repo-D"}),
        )
        # Synthetic training: 6 good cases, 5 diagnostic positives;
        # 6 bad cases, 4 correctly diagnostic negatives.
        self.rows = [
            record(i, "repo-A" if i % 2 == 0 else "repo-B",
                   1 if i < 6 else 0,
                   (i != 5) if i < 6 else (i >= 10))
            for i in range(12)
        ]

    def test_fit_exact_smoothed_counts(self):
        fit = fit_diagnostic_likelihood(self.rows, self.groups,
                                        "pinned-model", "test")
        self.assertEqual(fit.acceptable_n, 6)
        self.assertEqual(fit.unacceptable_n, 6)
        self.assertEqual(fit.train_group_count, 2)
        self.assertAlmostEqual(fit.sensitivity, 6 / 8)
        self.assertAlmostEqual(fit.specificity, 5 / 8)
        self.assertEqual(len(fit.training_fingerprint), 64)

    def test_train_fit_unchanged_by_record_order(self):
        x = fit_diagnostic_likelihood(self.rows, self.groups, "pinned-model", "test")
        y = fit_diagnostic_likelihood(list(reversed(self.rows)), self.groups,
                                      "pinned-model", "test")
        self.assertEqual(x, y)

    def test_no_evaluation_label_into_fit(self):
        for group in ("repo-C", "repo-D"):
            contaminated = self.rows + [record(100, group, 1, True)]
            with self.assertRaisesRegex(ValueError, "forbidden"):
                fit_diagnostic_likelihood(contaminated, self.groups,
                                           "pinned-model", "test")

    def test_no_unknown_group(self):
        with self.assertRaisesRegex(ValueError, "not assigned"):
            fit_diagnostic_likelihood(self.rows + [record(100, "fork-X", 0, False)],
                                      self.groups, "pinned-model", "test")

    def test_disjoint_lineage_groups_required(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            GroupPartitions(frozenset({"parent"}),
                            frozenset({"parent"}), frozenset({"heldout"}))
        with self.assertRaisesRegex(ValueError, "nonempty"):
            GroupPartitions(frozenset(), frozenset({"v"}), frozenset({"e"}))

    def test_duplicate_task_id_not_counted_twice(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            fit_diagnostic_likelihood(self.rows + [self.rows[0]], self.groups,
                                      "pinned-model", "test")

    def test_different_models_not_pooled(self):
        with self.assertRaisesRegex(ValueError, "cross-model"):
            fit_diagnostic_likelihood(self.rows + [record(100, "repo-A", 1, True,
                                                         model="other")],
                                      self.groups, "pinned-model", "test")

    def test_different_actions_not_pooled(self):
        with self.assertRaisesRegex(ValueError, "cross-model or cross-action"):
            fit_diagnostic_likelihood(self.rows + [record(100, "repo-B", 1, True,
                                                         action="static_analysis")],
                                      self.groups, "pinned-model", "test")

    def test_time_order_check_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "precede"):
            record(100, "repo-A", 1, True, evidence_time=200, oracle_time=100)
        with self.assertRaisesRegex(ValueError, "precede"):
            record(100, "repo-A", 1, True, evidence_time=200, oracle_time=200)

    def test_reject_malformed_observations(self):
        with self.assertRaises(ValueError):
            record(100, "repo-A", 1, 1)
        with self.assertRaises(ValueError):
            record(100, "repo-A", True, True)
        with self.assertRaises(ValueError):
            record(100, "repo-A", 2, False)
        with self.assertRaises(ValueError):
            record(100, "repo-A", 1, True, action="repair")

    def test_no_sparse_models_silently_fitted(self):
        sparse = self.rows[:5]
        with self.assertRaisesRegex(ValueError, "too few"):
            fit_diagnostic_likelihood(sparse, self.groups, "pinned-model", "test")

    def test_minimum_groups_stop(self):
        only_one_group = [record(i, "repo-A", int(i < 6), i < 6)
                          for i in range(12)]
        with self.assertRaisesRegex(ValueError, "too few independent"):
            fit_diagnostic_likelihood(only_one_group, self.groups,
                                      "pinned-model", "test")

    def test_no_empty_records(self):
        with self.assertRaisesRegex(ValueError, "no diagnostic"):
            fit_diagnostic_likelihood([], self.groups, "pinned-model", "test")

    def test_training_manifest_to_vector_policy_interface(self):
        model = fit_diagnostic_likelihood(self.rows, self.groups,
                                          "pinned-model", "test")
        forecast = model.forecast(ResourceVector(test_calls=1))
        self.assertEqual(forecast.action, "test")
        self.assertAlmostEqual(forecast.sensitivity, 0.75)
        self.assertEqual(forecast.cost.test_calls, 1)

    def test_frozen_training_likelihood_feeds_budgeted_planner(self):
        fitted = fit_diagnostic_likelihood(self.rows, self.groups,
                                           "pinned-model", "test")
        forecast = fitted.forecast(ResourceVector(test_calls=1))
        decision = choose_next_intervention(
            .85, [forecast],
            ResourceVector(tokens=5, test_calls=1, wall_seconds=5),
            ResourcePrices(test_calls=.05), ReleaseRule(.1))
        self.assertEqual(decision.action, "test")
        self.assertEqual(decision.budget_after.test_calls, 0)
        self.assertGreater(decision.predicted_net_improvement, 0)

    def test_invalid_minimum_and_smoothing(self):
        for kwargs in ({"minimum_per_class": 0},
                       {"minimum_groups": 1},
                       {"pseudocount": 0},
                       {"pseudocount": float("inf")}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                fit_diagnostic_likelihood(self.rows, self.groups,
                                          "pinned-model", "test", **kwargs)


if __name__ == "__main__":
    unittest.main()
