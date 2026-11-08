"""Offline synthetic falsification cases for lineage-omission ITT diagnostics."""
from dataclasses import asdict
from itertools import permutations
import json
import unittest

from ucode.evaluation import EvaluationOutcome, paired_verified_success
from ucode.lineage_influence import analyze_lineage_influence

T = "ucode_conditional_bes"
C = "no_uncertainty_search"


def pair(task, group, idx, tr, ct, *, model="model-a", seed=11, budget="cap-a"):
    """Two model-coded synthetic policies; 0=False release, 1=True release."""
    def record(policy, value):
        if value is None:
            return EvaluationOutcome(task, group, model, seed, budget, policy,
                                     False, None)
        return EvaluationOutcome(task, group, model, seed, budget, policy,
                                 True, bool(value))
    return (record(T, tr), record(C, ct))


def balanced_fixture():
    # 8 pairs: lineage A four +1, lineage B two -1, lineage C two 0;
    # full effect +0.25 but excluding A reverses to -0.5.
    rows = []
    for i in range(4):
        rows.extend(pair(f"A-{i}", "repo-A", i, 1, 0))
    for i in range(2):
        rows.extend(pair(f"B-{i}", "repo-B", i, 0, 1))
    for i in range(2):
        rows.extend(pair(f"C-{i}", "repo-C", i, 1, 1))
    return tuple(rows)


class LineageInfluenceTests(unittest.TestCase):
    def test_descriptive_effect_and_cluster_sign_reversal(self):
        result = analyze_lineage_influence(balanced_fixture(), T, C)
        self.assertEqual(result.paired_assignments, 8)
        self.assertEqual(result.nominal_lineage_groups, 3)
        self.assertEqual(result.observed_assignment_level_effect, .25)
        self.assertEqual(result.largest_lineage_assignment_fraction, .5)
        self.assertEqual(result.number_of_strict_sign_reversals, 1)
        a, b, c = result.leave_one_lineage_out
        self.assertEqual((a.lineage_group, a.omitted_pairs,
                          a.omitted_success_delta_sum, a.remaining_pairs),
                         ("repo-A", 4, 4, 4))
        self.assertAlmostEqual(a.effect_without_lineage, -.5)
        self.assertAlmostEqual(a.absolute_effect_shift, .75)
        self.assertTrue(a.strict_sign_reversal)
        self.assertAlmostEqual(b.effect_without_lineage, 4 / 6)
        self.assertAlmostEqual(c.effect_without_lineage, 2 / 6)
        self.assertEqual(result.maximum_absolute_effect_shift, .75)
        self.assertFalse(result.any_leave_one_lineage_effect_undefined)
        self.assertFalse(result.declares_independent_lineages_attested)
        self.assertFalse(result.certifies_real_model_experiment)

    def test_effect_equals_existing_paired_endpoint(self):
        data = balanced_fixture()
        official = paired_verified_success(data, T, C, bootstrap_samples=0)
        audit = analyze_lineage_influence(data, T, C)
        self.assertEqual(official.effect_success_difference,
                         audit.observed_assignment_level_effect)
        self.assertEqual(official.pairs, audit.paired_assignments)
        self.assertEqual(official.lineage_groups,
                         audit.nominal_lineage_groups)

    def test_single_lineage_leave_out_undefined_not_zero(self):
        data = pair("a", "same-repo", 0, 1, 0) + pair(
            "b", "same-repo", 1, 1, None
        )
        result = analyze_lineage_influence(data, T, C)
        self.assertEqual(result.paired_assignments, 2)
        self.assertEqual(result.nominal_lineage_groups, 1)
        self.assertEqual(result.observed_assignment_level_effect, 1)
        self.assertIsNone(result.maximum_absolute_effect_shift)
        self.assertTrue(result.any_leave_one_lineage_effect_undefined)
        r = result.leave_one_lineage_out[0]
        self.assertEqual(r.remaining_pairs, 0)
        self.assertIsNone(r.effect_without_lineage)
        self.assertIsNone(r.absolute_effect_shift)
        self.assertIsNone(r.strict_sign_reversal)

    def test_equal_task_weighting_even_for_unequal_clusters(self):
        data = balanced_fixture()
        result = analyze_lineage_influence(data, T, C)
        self.assertEqual(result.observed_assignment_level_effect, 2 / 8)
        self.assertNotEqual(result.observed_assignment_level_effect,
                            (1 + -1 + 0) / 3)

    def test_abstention_is_zero_in_assigned_task_denominator(self):
        data = pair("a", "a", 0, None, 1) + pair("b", "b", 0, 1, None)
        audit = analyze_lineage_influence(data, T, C)
        self.assertEqual(audit.paired_assignments, 2)
        self.assertEqual(audit.observed_assignment_level_effect, 0)
        self.assertEqual(audit.number_of_strict_sign_reversals, 0)
        self.assertTrue(all(x.strict_sign_reversal is False
                            for x in audit.leave_one_lineage_out))

    def test_stable_result_does_not_depend_on_receipt_order(self):
        src = balanced_fixture()
        reference = asdict(analyze_lineage_influence(src, T, C))
        for changed in (tuple(reversed(src)), src[::2]+src[1::2],
                        src[1::2]+src[::2]):
            self.assertEqual(asdict(analyze_lineage_influence(changed, T, C)),
                             reference)

    def test_duplicate_pair_rejected(self):
        data = balanced_fixture()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            analyze_lineage_influence(data + (data[0],), T, C)

    def test_missing_one_policy_rejected(self):
        data = balanced_fixture()
        with self.assertRaisesRegex(ValueError, "unmatched"):
            analyze_lineage_influence(data[:-1], T, C)

    def test_same_task_switches_lineage_between_policies_rejected(self):
        left, right = pair("a", "family-A", 0, 1, 0)
        changed = EvaluationOutcome("a", "family-B", right.model_id, right.seed,
                                    right.budget_id, right.policy,
                                    right.released, right.oracle_passed)
        with self.assertRaisesRegex(ValueError, "fork group"):
            analyze_lineage_influence((left,changed), T, C)

    def test_task_identity_switches_lineage_between_seeds_rejected(self):
        left = pair("a", "family-A", 0, 1, 0, seed=1)
        right = pair("a", "family-B", 0, 0, 1, seed=2)
        with self.assertRaisesRegex(ValueError, "fork group"):
            analyze_lineage_influence(left + right, T, C)

    def test_no_silent_baseline_change(self):
        with self.assertRaisesRegex(ValueError, "distinct"):
            analyze_lineage_influence(balanced_fixture(), T, T)

    def test_wrong_policy_label_rejected(self):
        data = list(balanced_fixture())
        bad = EvaluationOutcome("foreign", "g", "model", 11, "budget",
                                "unexpected", True, True)
        with self.assertRaisesRegex(ValueError, "only two"):
            analyze_lineage_influence(tuple(data+[bad]), T, C)

    def test_malformed_oracle_record_rejected(self):
        data = balanced_fixture()
        for invalid in ({"fake": True}, "actual success=1", None):
            with self.subTest(invalid=invalid), self.assertRaises(TypeError):
                analyze_lineage_influence(data + (invalid,), T, C)

    def test_model_seed_budget_repeated_assignments_count_as_pairs(self):
        a = pair("t", "lineage", 0, 1, 0, seed=11)
        b = pair("t", "lineage", 0, 0, 1, seed=29)
        c = pair("t", "lineage", 0, 1, 1, model="other")
        d = pair("t", "different", 0, 0, 1, budget="expensive")
        # d is prohibited: same task identity cannot split family, even
        # across budgets. Correct the family for a valid four-pair case.
        d = pair("t", "lineage", 0, 0, 1, budget="expensive")
        report = analyze_lineage_influence(a+b+c+d, T, C)
        self.assertEqual(report.paired_assignments, 4)
        self.assertEqual(report.nominal_lineage_groups, 1)
        self.assertEqual(report.observed_assignment_level_effect, -.25)

    def test_invalid_sequence_type_and_empty_data_rejected(self):
        for bad in (None, "bad", {}, iter(balanced_fixture())):
            with self.subTest(bad=type(bad)), self.assertRaises(TypeError):
                analyze_lineage_influence(bad, T, C)
        with self.assertRaisesRegex(ValueError, "nonempty"):
            analyze_lineage_influence((), T, C)

    def test_full_report_can_serialize_without_raw_oracle_text(self):
        report = analyze_lineage_influence(balanced_fixture(), T, C)
        payload = json.dumps(asdict(report), sort_keys=True)
        self.assertIn("lineage_group", payload)
        self.assertNotIn("oracle_passed", payload)
        self.assertNotIn("patch_sha256", payload)
        self.assertNotIn("secret", payload)


if __name__ == "__main__":
    unittest.main()
