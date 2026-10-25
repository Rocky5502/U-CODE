"""SYNTHETIC postterminal attrition bounds, not empirical U-CODE effects."""
from dataclasses import replace
import unittest

from ucode.attrition_bounds import paired_effect_attrition_bounds
from ucode.experiment_contract import (
    EvaluatorVerdict, FrozenStudy, PolicyRunReceipt,
    audit_confirmatory_run_matrix,
)
from ucode.vector_policy import ResourceVector


def fixture():
    study = FrozenStudy(
        (("a", "fork-a"), ("b", "fork-b")),
        ("frozen-model",), ("ucode", "baseline"),
        (17,), (("budget", ResourceVector(tokens=100, test_calls=2,
                      gpu_seconds=2, cpu_seconds=5, wall_seconds=10)),),
    )
    term = {
        ("a", "ucode"): "release",
        ("a", "baseline"): "infrastructure_failure",
        ("b", "ucode"): "timeout",
        ("b", "baseline"): "release",
    }
    receipts, verdicts = [], []
    for task,group in study.task_lineages:
        for policy in study.policies:
            status = term[(task,policy)]
            r = PolicyRunReceipt(
                task, group, "frozen-model", policy, 17, "budget",
                "b"*40, "c"*40, "d"*64, "e"*64,
                ResourceVector(tokens=20, test_calls=1, wall_seconds=5),
                status, "a"*64 if status == "release" else None, "f"*64,
            )
            receipts.append(r)
            if status == "release":
                verdicts.append(EvaluatorVerdict(
                    task, "frozen-model", policy, 17, "budget",
                    "a"*64, "1"*64, True, "2"*64))
    return study, tuple(receipts), tuple(verdicts)


class AttritionBoundsTests(unittest.TestCase):
    def setUp(self):
        self.study, self.records, self.verdicts = fixture()

    def bound(self, recs=None, gold=None):
        return paired_effect_attrition_bounds(
            self.study, self.records if recs is None else recs,
            self.verdicts if gold is None else gold, "ucode", "baseline",
        )

    def test_worst_best_bounds_keep_infra_unknown(self):
        b=self.bound()
        self.assertEqual(b.assigned_pairs, 2)
        self.assertEqual(b.known_pair_differences, 1)
        self.assertEqual(b.partially_observed_pairs, 1)
        self.assertEqual(b.infrastructure_failure_cells, 1)
        self.assertAlmostEqual(b.lower_effect,-.5)
        self.assertAlmostEqual(b.upper_effect,0)
        self.assertFalse(b.point_identified)

    def test_timeout_fails_full_task_success_not_dropped(self):
        b=self.bound()
        self.assertEqual(b.timeouts_as_nonrelease_failures,1)
        self.assertEqual(b.assigned_pairs,2)

    def test_all_terminal_receipts_yield_exact_effect(self):
        changed=(self.records[0],
                 replace(self.records[1], termination="abstain"),
                 replace(self.records[2], termination="abstain"),
                 self.records[3])
        b=self.bound(changed)
        self.assertTrue(b.point_identified)
        self.assertAlmostEqual(b.lower_effect,0)
        self.assertEqual(b.partially_observed_pairs,0)

    def test_both_infrastructure_failures_span_a_full_pair_unit(self):
        changed=(replace(self.records[0],termination="infrastructure_failure",
                         patch_sha256=None),
                 self.records[1],self.records[2],self.records[3])
        v=tuple(x for x in self.verdicts if x.key != self.records[0].key)
        b=self.bound(changed,v)
        self.assertEqual(b.infrastructure_failure_cells,2)
        self.assertEqual(b.partially_observed_pairs,1)
        self.assertEqual(b.lower_effect,-1.0)
        self.assertEqual(b.upper_effect,0.0)

    def test_unknown_outcome_always_bounded_valid_effect_range(self):
        b=self.bound()
        self.assertTrue(-1<=b.lower_effect<=b.upper_effect<=1)

    def test_unmatched_policy_receipt_cannot_disappear(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.bound(self.records[:-1])

    def test_infrastructure_failure_cannot_keep_a_gold_verdict(self):
        v=EvaluatorVerdict("a","frozen-model","baseline",17,"budget",
                           "a"*64,"1"*64,False,"2"*64)
        with self.assertRaisesRegex(ValueError,"abstained, failed"):
            self.bound(gold=self.verdicts+(v,))

    def test_wrong_patch_digest_fails_oracle_join(self):
        alt=replace(self.verdicts[0],patch_sha256="7"*64)
        with self.assertRaisesRegex(ValueError,"different from released"):
            self.bound(gold=(alt,)+self.verdicts[1:])

    def test_over_budget_receipt_fails_before_any_effect(self):
        z=replace(self.records[0],
                  consumed=ResourceVector(tokens=101))
        with self.assertRaisesRegex(ValueError,"FIVE-resource"):
            self.bound(recs=(z,)+self.records[1:])

    def test_treatment_and_comparator_must_be_different_registered_policies(self):
        with self.assertRaisesRegex(ValueError, "distinct preregistered"):
            paired_effect_attrition_bounds(self.study,self.records,self.verdicts,
                                           "ucode","ucode")
        with self.assertRaisesRegex(ValueError, "distinct preregistered"):
            paired_effect_attrition_bounds(self.study,self.records,self.verdicts,
                                           "ucode","not-pre-registered")

    def test_nonrelease_safety_stop_counts_failure_not_oracle(self):
        recs=(self.records[0],
              replace(self.records[1], termination="safety_block"),
              self.records[2], self.records[3])
        b=self.bound(recs)
        self.assertEqual(b.safety_blocks_as_nonrelease_failures,1)
        self.assertEqual(b.lower_effect,b.upper_effect)
        self.assertEqual(b.lower_effect,0)

    def test_real_evaluator_approval_not_implied_by_bounds(self):
        b=self.bound()
        self.assertIn("not_confidence_interval",b.interval_kind)
        self.assertEqual(b.assigned_pairs,2)


if __name__=="__main__":
    unittest.main()
