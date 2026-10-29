"""Train-only conditional likelihood fit on invented FULL-PANEL traces.

The synthetic rows exercise schema and leakage properties, not model
calibration, realistic test dependence or correctness verification.
"""
from dataclasses import replace
import unittest

from ucode.conditional_fit import (
    FullPanelTrainingTrace, fit_history_conditional_kernel,
)
from ucode.conditional_bes import (
    ConditionalProbe, ConditionalState, Observation, plan_conditional,
)
from ucode.diagnostic_fit import GroupPartitions
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


def panel(i, group, order, signs, label, model="frozen-model"):
    return FullPanelTrainingTrace(
        f"fixture-{i}", group, model, order, signs,
        (10, 20), label, 30, f"oracle-{i}",
    )


class HistoryConditionalFittingTests(unittest.TestCase):
    def setUp(self):
        self.partitions = GroupPartitions(frozenset(("g1", "g2")),
                                          frozenset(("hold-val",)),
                                          frozenset(("hold-test",)))
        self.actions = ("a", "b")
        self.rows = []
        for order in (("a", "b"), ("b", "a")):
            for label in (0, 1):
                for first in (False, True):
                    for second in (False, True):
                        group = "g1" if second else "g2"
                        self.rows.append(panel(
                            len(self.rows), group, order, (first, second),
                            label,
                        ))

    def fit(self, rows=None, **kw):
        return fit_history_conditional_kernel(
            self.rows if rows is None else rows, self.partitions,
            "frozen-model", self.actions, **kw)

    def test_per_context_and_per_label_lineage_support_is_reported(self):
        result = self.fit()
        self.assertEqual(result.minimum_lineages_per_context_class, 2)
        self.assertEqual(result.weakest_class_context_lineages, 2)

    def test_global_lineage_coverage_cannot_mask_sparse_history_class(self):
        # Distinct lineages survive globally and in every root row.
        # But (action=b, first observation a=True, Y=1) is now from g1
        # alone. The old fitter accepted it with minimum_per_class=1.
        rows = [
            r for r in self.rows
            if not (r.action_order == ("a", "b")
                    and r.oracle_acceptable == 1
                    and r.outcomes[0] is True
                    and r.lineage_group == "g2")
        ]
        self.assertEqual(len({r.lineage_group for r in rows}), 2)
        with self.assertRaisesRegex(
                ValueError, "lineages per conditional context"):
            self.fit(rows)

    def test_structured_history_hash_distinguishes_separator_aliases(self):
        from dataclasses import replace
        p = GroupPartitions(
            frozenset(("g1", "g2", "x", "g1|x")),
            frozenset(("hold-val",)), frozenset(("hold-test",)))
        candidate = panel(999, "x", ("a", "b"), (True, False), 1)
        x = replace(candidate, task_id="new|g1", lineage_group="x")
        y = replace(candidate, task_id="new", lineage_group="g1|x")
        left = fit_history_conditional_kernel(
            self.rows + [x], p, "frozen-model", self.actions)
        right = fit_history_conditional_kernel(
            self.rows + [y], p, "frozen-model", self.actions)
        self.assertNotEqual(left.input_fingerprint, right.input_fingerprint)

    def test_reject_invalid_per_context_lineage_threshold(self):
        for bad in (0, 1, True):
            with self.subTest(bad=bad), self.assertRaisesRegex(
                    ValueError, "minimum_lineages_per_context_class"):
                self.fit(minimum_lineages_per_context_class=bad)

    def test_full_panel_invented_fixture_estimates_six_contexts(self):
        manifest = self.fit()
        self.assertEqual(manifest.training_task_count, 16)
        self.assertEqual(manifest.lineage_count, 2)
        self.assertEqual(manifest.context_count, 6)
        self.assertEqual(len(manifest.input_fingerprint), 64)
        self.assertAlmostEqual(manifest.kernel.get("a", ()).positive_if_acceptable, .5)
        self.assertAlmostEqual(
            manifest.kernel.get("b", (Observation("a", True),)).
            positive_if_unacceptable, .5)

    def test_fit_deterministic_to_task_row_order(self):
        self.assertEqual(self.fit(), self.fit(list(reversed(self.rows))))

    def test_output_plugs_into_conditional_planner(self):
        m = self.fit()
        probes = [ConditionalProbe("a", "test", ResourceVector(test_calls=1)),
                  ConditionalProbe("b", "test", ResourceVector(test_calls=1))]
        result = plan_conditional(
            ConditionalState(.5, ResourceVector(test_calls=2)),
            probes, m.kernel, ResourcePrices(test_calls=.01),
            ReleaseRule(.1), horizon=2)
        self.assertEqual(result.action, "abstain")

    def test_eval_and_validation_label_leakage_refused(self):
        for g in ("hold-val", "hold-test"):
            contaminated = self.rows + [panel(999, g, ("a", "b"),
                                             (True, False), 1)]
            with self.assertRaisesRegex(ValueError, "forbidden"):
                self.fit(contaminated)

    def test_unassigned_fork_lineage_rejected(self):
        contaminated = self.rows + [panel(999, "unseen-fork", ("a", "b"),
                                         (False, False), 0)]
        with self.assertRaisesRegex(ValueError, "not assigned"):
            self.fit(contaminated)

    def test_different_model_and_duplicate_task_refused(self):
        with self.assertRaisesRegex(ValueError, "distinct model"):
            self.fit(self.rows + [panel(999, "g1", ("a", "b"),
                                             (True, False), 1, model="other")])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.fit(self.rows + [self.rows[0]])

    def test_no_adaptive_action_selection_claims(self):
        with self.assertRaisesRegex(ValueError, "adaptive"):
            replace(self.rows[0], assignment_protocol="adaptive_selective")
        with self.assertRaisesRegex(ValueError, "full action panel"):
            self.fit(self.rows + [replace(
                self.rows[0], task_id="extra",
                action_order=("a", "c"),
            )])

    def test_sparse_conditional_context_fails_instead_of_backoff(self):
        missing = [row for row in self.rows if not (
            row.action_order == ("a", "b") and
            row.oracle_acceptable == 1 and
            row.outcomes[0] is True)]
        with self.assertRaisesRegex(ValueError, "sparse"):
            self.fit(missing)

    def test_timestamps_precede_training_oracle_and_strict_order(self):
        with self.assertRaisesRegex(ValueError, "pre-oracle"):
            replace(self.rows[0], visible_times=(20, 10))
        with self.assertRaisesRegex(ValueError, "pre-oracle"):
            replace(self.rows[0], visible_times=(10, 30))

    def test_observations_must_be_complete_and_binary(self):
        with self.assertRaisesRegex(ValueError, "full panel"):
            replace(self.rows[0], outcomes=(True,))
        with self.assertRaisesRegex(ValueError, "booleans"):
            replace(self.rows[0], outcomes=(1, False))
        with self.assertRaisesRegex(ValueError, "0/1"):
            replace(self.rows[0], oracle_acceptable=True)

    def test_invalid_fit_hyperparameters_fail(self):
        for kwargs in (
            {"minimum_per_class": 0},
            {"minimum_lineages": 1},
            {"pseudocount": 0},
            {"pseudocount": float("nan")},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.fit(**kwargs)

    def test_no_real_oracle_guarantee_is_claimed(self):
        self.assertEqual(self.fit().status,
                         "training_only_not_independently_validated")
        with self.assertRaisesRegex(ValueError, "no training"):
            self.fit([])

    def test_reject_incomplete_two_research_groups(self):
        rows = [r for r in self.rows if r.lineage_group == "g1"]
        with self.assertRaisesRegex(ValueError, "lineages"):
            self.fit(rows)

    def test_supports_only_one_to_four_distinct_probe_ids(self):
        for ids in ((), ("a", "a"), ("a", "b", "c", "d", "e")):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                fit_history_conditional_kernel(
                    self.rows, self.partitions, "frozen-model", ids)


if __name__ == "__main__":
    unittest.main()
