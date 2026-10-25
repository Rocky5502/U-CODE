"""First-party SYNTHETIC receipts for software-engineering evaluation gates."""
from dataclasses import replace
import unittest

from ucode.experiment_contract import (
    EvaluatorVerdict, FrozenStudy, PolicyRunReceipt,
    audit_confirmatory_run_matrix, compare_matched_policies,
)
from ucode.vector_policy import ResourceVector


def fixture():
    study = FrozenStudy(
        (("task-a", "repo-group-a"), ("task-b", "repo-group-b")),
        ("model-one", "model-two"),
        ("ucode", "no-uncertainty"),
        (11, 17),
        (("tiny", ResourceVector(tokens=120, test_calls=3,
                                 gpu_seconds=20, cpu_seconds=40,
                                 wall_seconds=50)),),
    )
    runs, verdicts = [], []
    for task, lineage in study.task_lineages:
        for model in study.model_ids:
            for seed in study.seeds:
                for policy in study.policies:
                    releasing = (policy == "ucode" or seed == 11)
                    patch = "a"*64 if releasing else None
                    r = PolicyRunReceipt(
                        task, lineage, model, policy, seed, "tiny",
                        "c"*40,
                        ResourceVector(tokens=100 if policy=="ucode" else 80,
                                       test_calls=3 if policy=="ucode" else 1,
                                       gpu_seconds=10, cpu_seconds=20,
                                       wall_seconds=25),
                        "release" if releasing else "abstain",
                        patch, "b"*64,
                    )
                    runs.append(r)
                    if releasing:
                        # Invented oracle responses, never real model results:
                        success = policy == "ucode" or task == "task-a"
                        verdicts.append(EvaluatorVerdict(
                            task, model, policy, seed, "tiny", patch,
                            "d"*64, success, "e"*64))
    return study, tuple(runs), tuple(verdicts)


class StrictEmpiricalContractTests(unittest.TestCase):
    def setUp(self):
        self.study, self.runs, self.verdicts = fixture()

    def audit(self, runs=None, verdicts=None, study=None, **kwargs):
        return audit_confirmatory_run_matrix(
            self.study if study is None else study,
            self.runs if runs is None else runs,
            self.verdicts if verdicts is None else verdicts,
            **kwargs,
        )

    def test_complete_paired_matrix_and_oracle_count(self):
        a = self.audit()
        self.assertEqual(a.expected_runs, 16)
        self.assertEqual(a.observed_runs, 16)
        self.assertEqual(a.verified_oracle_receipts, 12)
        self.assertEqual(a.incomplete_terminations, 0)
        self.assertEqual(len(a.outcomes), 16)

    def test_same_budget_ceiling_but_different_actual_expenditure(self):
        a = self.audit()
        spend = dict(a.consumed_by_policy)
        self.assertEqual(spend["ucode"].tokens, 800)
        self.assertEqual(spend["no-uncertainty"].tokens, 640)
        self.assertEqual(spend["ucode"].test_calls, 24)
        self.assertEqual(spend["no-uncertainty"].test_calls, 8)

    def test_confirmatory_pair_synthetic_effect_and_coverage(self):
        a, b, d = compare_matched_policies(
            self.audit(), "ucode", "no-uncertainty",
            bootstrap_samples=200, seed=42,
        )
        self.assertEqual(a.attempts, 8)
        self.assertEqual(a.successes, 8)
        self.assertEqual(a.coverage, 1)
        self.assertEqual(b.attempts, 8)
        self.assertEqual(b.successes, 2)
        self.assertEqual(b.releases, 4)
        self.assertEqual(b.wrong_release_risk, .5)
        self.assertEqual(d.pairs, 8)
        self.assertAlmostEqual(d.effect_success_difference, .75)
        self.assertEqual(d.lineage_groups, 2)
        self.assertIsNotNone(d.cluster_bootstrap_ci_95)

    def test_missing_one_run_fails_not_complete_case(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.audit(runs=self.runs[1:])

    def test_duplicate_run_fails_not_double_weighted(self):
        with self.assertRaisesRegex(ValueError, "duplicated"):
            self.audit(runs=self.runs[:-1]+(self.runs[0],))

    def test_one_wrong_model_is_rejected(self):
        r = replace(self.runs[0], model_id="substituted")
        with self.assertRaisesRegex(ValueError, "wrong models"):
            self.audit(runs=(r,)+self.runs[1:])

    def test_repo_fork_lineage_switch_rejected(self):
        r = replace(self.runs[0], lineage_group="different-fork")
        with self.assertRaisesRegex(ValueError, "wrong repository"):
            self.audit(runs=(r,)+self.runs[1:])

    def test_over_budget_one_resource_rejected_even_other_resources_fine(self):
        r = replace(self.runs[0], consumed=ResourceVector(
            tokens=110, test_calls=4, gpu_seconds=1,
            cpu_seconds=1, wall_seconds=1))
        with self.assertRaisesRegex(ValueError, "FIVE-resource"):
            self.audit(runs=(r,)+self.runs[1:])

    def test_budget_vector_nonzero_and_tuple_factors_mandatory(self):
        with self.assertRaisesRegex(ValueError, "nonzero"):
            FrozenStudy(self.study.task_lineages, self.study.model_ids,
                        self.study.policies, self.study.seeds,
                        (("tiny", ResourceVector()),))
        with self.assertRaisesRegex(ValueError, "nonempty"):
            FrozenStudy((), self.study.model_ids, self.study.policies,
                        self.study.seeds, self.study.budgets)

    def test_duplicate_model_policy_task_seed_and_budget_rejected(self):
        for change in (
            {"model_ids": ("model-one", "model-one")},
            {"policies": ("ucode", "ucode")},
            {"task_lineages": (("task-a","repo-a"), ("task-a","repo-b"))},
            {"seeds": (11, 11)},
            {"budgets": self.study.budgets + self.study.budgets},
        ):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "duplicate"):
                replace(self.study, **change)

    def test_release_requires_patch_content_hash(self):
        with self.assertRaisesRegex(ValueError, "released patch"):
            replace(self.runs[0], patch_sha256=None)
        with self.assertRaisesRegex(ValueError, "released patch"):
            replace(self.runs[0], patch_sha256="branch-main")

    def test_abstention_cannot_carry_release_patch(self):
        with self.assertRaisesRegex(ValueError, "must not contain"):
            replace(self.runs[0], termination="abstain")

    def test_oracle_must_match_exact_released_patch_digest(self):
        forged = replace(self.verdicts[0], patch_sha256="9"*64)
        with self.assertRaisesRegex(ValueError, "different from released"):
            self.audit(verdicts=(forged,)+self.verdicts[1:])

    def test_oracle_cannot_label_abstention(self):
        abstained = next(x for x in self.runs if x.termination == "abstain")
        injected = EvaluatorVerdict(
            abstained.task_id, abstained.model_id,
            abstained.policy, abstained.seed, abstained.budget_id,
            "a"*64, "d"*64, False, "e"*64)
        with self.assertRaisesRegex(ValueError, "abstained"):
            self.audit(verdicts=self.verdicts + (injected,))

    def test_missing_gold_for_release_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "lacks"):
            self.audit(verdicts=self.verdicts[:-1])

    def test_duplicate_oracle_verdict_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate evaluator"):
            self.audit(verdicts=self.verdicts+(self.verdicts[0],))

    def test_receipt_has_no_gold_field(self):
        with self.assertRaises(TypeError):
            PolicyRunReceipt(**{**self.runs[0].__dict__, "oracle_passed": True})
        self.assertNotIn("oracle_passed", self.runs[0].__dict__)

    def test_assumed_instead_of_measured_costs_rejected(self):
        with self.assertRaisesRegex(ValueError, "measured costs"):
            replace(self.runs[0], actual_costs_measured=False)

    def test_missing_policy_log_hash_rejected(self):
        with self.assertRaisesRegex(ValueError, "policy log"):
            replace(self.runs[0], visible_policy_log_sha256="bad")

    def test_truthy_non_boolean_oracle_result_rejected(self):
        with self.assertRaisesRegex(ValueError, "boolean"):
            replace(self.verdicts[0], oracle_passed=1)

    def test_timeout_must_be_reported_and_blocks_silent_success_inference(self):
        r = replace(self.runs[0], termination="timeout", patch_sha256=None)
        records=(r,)+self.runs[1:]
        values=tuple(v for v in self.verdicts if v.key != self.runs[0].key)
        with self.assertRaisesRegex(ValueError, "attrition"):
            self.audit(runs=records, verdicts=values)
        report=self.audit(runs=records, verdicts=values, require_complete=False)
        self.assertEqual(report.incomplete_terminations, 1)
        self.assertEqual(dict(report.by_failure_reason)["timeout"], 1)
        self.assertEqual(report.outcomes, ())
        with self.assertRaisesRegex(ValueError, "attrition"):
            compare_matched_policies(report,"ucode","no-uncertainty")

    def test_infra_and_safety_stop_separated_from_abstention(self):
        r1 = replace(self.runs[0], termination="infrastructure_failure", patch_sha256=None)
        r2 = replace(self.runs[1], termination="safety_block", patch_sha256=None)
        keep = {self.runs[0].key, self.runs[1].key}
        v = tuple(x for x in self.verdicts if x.key not in keep)
        report=self.audit(runs=(r1,r2)+self.runs[2:], verdicts=v, require_complete=False)
        self.assertEqual(dict(report.by_failure_reason)["infrastructure_failure"], 1)
        self.assertEqual(dict(report.by_failure_reason)["safety_block"], 1)

    def test_outside_protocol_label_does_not_enter_analysis(self):
        v = replace(self.verdicts[0], task_id="new-task")
        with self.assertRaisesRegex(ValueError, "unassigned"):
            self.audit(verdicts=(v,)+self.verdicts[1:])

    def test_requiring_both_policies_for_difference(self):
        with self.assertRaisesRegex(ValueError, "absent"):
            compare_matched_policies(self.audit(), "ucode","absent")

    def test_no_false_empirical_claims_generated_from_empty_dataset(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            FrozenStudy((),("real-model",),("ucode",),(42,),
                        (("B",ResourceVector(tokens=10)),))

    def test_wrong_integer_seed_rejected(self):
        with self.assertRaisesRegex(ValueError, "seed"):
            replace(self.runs[0], seed=True)
        with self.assertRaisesRegex(ValueError, "seed"):
            replace(self.verdicts[0], seed=-1)

    def test_same_task_across_policies_has_equal_budget_assignment(self):
        study,r,v=fixture()
        caps=dict(study.budgets)
        self.assertEqual(set(t.budget_id for t in r), {"tiny"})
        self.assertTrue(all(caps[t.budget_id].affordable(t.consumed) for t in r))


if __name__=="__main__":
    unittest.main()
