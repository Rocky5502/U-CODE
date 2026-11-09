"""S03 first-party falsification: six objectives, fixed caps, exact union HV.

Every example is SYNTHETIC. Fabricated patch hashes, resource usage and oracle
verdicts do not create model evidence, verified meters or runnable benchmarks.
"""
from dataclasses import asdict, replace
from itertools import combinations
from math import prod
from random import Random
import json
import unittest

from ucode.experiment_contract import (
    EvaluatorVerdict, FrozenStudy, PolicyRunReceipt,
)
from ucode.matched_pareto_audit import (
    MAX_PARETO_POLICIES, ParetoArm, audit_matched_postterminal_pareto,
    audit_resource_quality_frontier, dominates,
)
from ucode.vector_policy import RESOURCE_FIELDS, ResourceVector as RV


UNIT_CAP = RV(tokens=10, test_calls=10, gpu_seconds=10,
              cpu_seconds=10, wall_seconds=10)
USED_A = RV(tokens=1, test_calls=1, gpu_seconds=1,
            cpu_seconds=1, wall_seconds=1)
USED_B = RV(tokens=2, test_calls=2, gpu_seconds=2,
            cpu_seconds=2, wall_seconds=2)


def v(**kwargs):
    return RV(**kwargs)


def point(name, quality, cost):
    return ParetoArm(name, quality, cost)


def synthetic_matrix(*, state="complete"):
    """Two tasks x 2 policies; original fixed assignment denominator N=2."""
    study = FrozenStudy(
        (("fake-task-1", "fake-fork-1"), ("fake-task-2", "fake-fork-2")),
        ("fake-model",), ("treatment", "baseline"), (7,),
        (("fake-budget", UNIT_CAP),),
    )
    receipts = []
    verdicts = []
    for i, (task, family) in enumerate(study.task_lineages):
        for policy in study.policies:
            termination = "release" if policy == "treatment" or i == 0 else "abstain"
            if state == "infra" and i == 0 and policy == "baseline":
                termination = "infrastructure_failure"
            if state == "timeout" and i == 1 and policy == "treatment":
                termination = "timeout"
            patch = format(10 * i + (1 if policy == "treatment" else 2), "064x")
            cost = (RV(tokens=1 if i == 0 else 2,
                       test_calls=1 if i == 0 else 2,
                       gpu_seconds=1, cpu_seconds=1, wall_seconds=1)
                    if policy == "treatment" else USED_B)
            receipt = PolicyRunReceipt(
                task_id=task, lineage_group=family, model_id="fake-model",
                policy=policy, seed=7, budget_id="fake-budget",
                pre_fix_base_sha="a" * 40,
                model_checkpoint_sha40="b" * 40,
                tool_access_sha256="c" * 64,
                environment_image_sha256="d" * 64,
                consumed=cost, termination=termination,
                patch_sha256=patch if termination == "release" else None,
                visible_policy_log_sha256="e" * 64,
            )
            receipts.append(receipt)
            if termination == "release":
                verdicts.append(EvaluatorVerdict(
                    task_id=task, model_id="fake-model", policy=policy,
                    seed=7, budget_id="fake-budget",
                    patch_sha256=patch,
                    oracle_artifact_sha256=format(i+10, "064x"),
                    oracle_passed=(policy == "treatment" or i == 0),
                    evaluator_log_sha256="f" * 64,
                ))
    return study, tuple(receipts), tuple(verdicts)


def audit_synthetic(study, receipts, verdicts):
    return audit_matched_postterminal_pareto(
        study, receipts, verdicts,
        model_id="fake-model", budget_id="fake-budget",
    )


def independent_inclusion_exclusion_hv(arms, cap, n=1):
    """Independent finite geometric reference, NOT the recursive sweep."""
    coords = []
    for p in arms:
        gains = (p.evaluator_claimed_success_rate,) + tuple(
            1 - getattr(p.total_reported_cost, k) / (getattr(cap, k) * n)
            for k in RESOURCE_FIELDS)
        coords.append(gains)
    answer = 0.
    for size in range(1, len(coords) + 1):
        for subset in combinations(coords, size):
            volume = prod(min(p[dim] for p in subset) for dim in range(6))
            answer += volume if size % 2 else -volume
    return answer


class MatchedParetoTests(unittest.TestCase):
    def test_six_objectives_five_caps_never_scalarized(self):
        x = audit_resource_quality_frontier(
            (point("one", .8, USED_A),), UNIT_CAP, 1)
        self.assertEqual(x.six_objectives[0],
                         "claimed_full_task_success_maximize")
        self.assertEqual(len(x.six_objectives), 6)
        self.assertTrue(all(key in x.six_objectives[1:]
                            for key in ("reported_"+k+"_minimize"
                                        for k in RESOURCE_FIELDS)))
        self.assertAlmostEqual(x.exact_normalized_hypervolume,
                               .8 * .9**5)
        self.assertFalse(x.reported_costs_independently_measured)
        self.assertFalse(x.hidden_oracles_independently_authenticated)
        self.assertFalse(x.licensed_models_and_tasks_qualified)
        self.assertFalse(x.real_experiment_approved)

    def test_strong_dominance_identifies_all_six_axes(self):
        better = point("better", 1., USED_A)
        worse = point("worse", .5, USED_B)
        self.assertTrue(dominates(better, worse))
        self.assertFalse(dominates(worse, better))
        x = audit_resource_quality_frontier((worse, better), UNIT_CAP, 1)
        self.assertEqual(x.nondominated_policies, ("better",))
        self.assertEqual(dict(x.dominated_by)["worse"], ("better",))
        self.assertAlmostEqual(x.exact_normalized_hypervolume, .9**5)
        self.assertAlmostEqual(dict(x.marginal_hypervolume_by_policy)["worse"], 0.)

    def test_unequal_resources_and_quality_are_true_pareto_tradeoffs(self):
        a = point("a", .8, v(tokens=2,test_calls=8,gpu_seconds=8,
                              cpu_seconds=8,wall_seconds=8))
        b = point("b", .6, v(tokens=8,test_calls=2,gpu_seconds=2,
                              cpu_seconds=2,wall_seconds=2))
        x = audit_resource_quality_frontier((b, a), UNIT_CAP, 1)
        self.assertEqual(x.nondominated_policies, ("a", "b"))
        self.assertEqual(x.dominated_by, (("a", ()), ("b", ())))
        expected = (.8*.8*.2**4 + .6*.2*.8**4 - .6*.2**5)
        self.assertAlmostEqual(x.exact_normalized_hypervolume, expected)
        self.assertGreater(dict(x.marginal_hypervolume_by_policy)["a"], 0)
        self.assertGreater(dict(x.marginal_hypervolume_by_policy)["b"], 0)

    def test_duplicate_quality_and_cost_ties_not_double_counted(self):
        p = point("a", .75, USED_A)
        q = point("b", .75, USED_A)
        single = audit_resource_quality_frontier((p,), UNIT_CAP, 1)
        duplicated = audit_resource_quality_frontier((q,p), UNIT_CAP, 1)
        self.assertEqual(duplicated.nondominated_policies, ("a","b"))
        self.assertEqual(duplicated.identical_tradeoff_ties, (("a","b"),))
        self.assertEqual(duplicated.exact_normalized_hypervolume,
                         single.exact_normalized_hypervolume)
        self.assertEqual(dict(duplicated.marginal_hypervolume_by_policy),
                         {"a":0.,"b":0.})

    def test_zero_quality_has_zero_volume_but_remains_nondominated(self):
        p = point("zero-quality", 0., RV())
        x = audit_resource_quality_frontier((p,), UNIT_CAP, 1)
        self.assertEqual(x.exact_normalized_hypervolume, 0.)
        self.assertEqual(x.nondominated_policies, ("zero-quality",))

    def test_exact_cap_consumption_has_zero_hypervolume(self):
        x = audit_resource_quality_frontier(
            (point("fully-used", 1., UNIT_CAP),), UNIT_CAP, 1)
        self.assertEqual(x.exact_normalized_hypervolume, 0.)
        self.assertEqual(x.nondominated_policies, ("fully-used",))

    def test_one_resource_cap_violation_never_hidden_by_four_savings(self):
        for field in RESOURCE_FIELDS:
            spent = {k:0 for k in RESOURCE_FIELDS}
            spent[field] = 11 if field in ("tokens","test_calls") else 10.1
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "FIVE-resource cap: "+field):
                audit_resource_quality_frontier(
                    (point("bad", 1., RV(**spent)),), UNIT_CAP, 1)

    def test_all_five_zero_cap_dimensions_fail_closed(self):
        for field in RESOURCE_FIELDS:
            caps = {k:10 for k in RESOURCE_FIELDS}
            caps[field] = 0
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "strictly positive"):
                audit_resource_quality_frontier(
                    (point("a", .5, RV()),), RV(**caps), 1)

    def test_fractional_mean_tokens_are_handled_as_integral_totals(self):
        # Across two assigned runs: cost 3 tokens, average 1.5; never
        # pretend a 1.5-token *individual* receipt is a valid reading.
        p = point("a", 1., v(tokens=3,test_calls=3,gpu_seconds=3,
                             cpu_seconds=3,wall_seconds=3))
        x = audit_resource_quality_frontier((p,), UNIT_CAP, 2)
        self.assertEqual(x.matched_assignments_per_policy, 2)
        self.assertAlmostEqual(x.exact_normalized_hypervolume,
                               (1 - 3/20) ** 5)
        with self.assertRaisesRegex(ValueError, "whole number"):
            RV(tokens=1.5)

    def test_correlated_five_resource_profiles_not_assumed_independent(self):
        a = point("a", .9, v(tokens=1,test_calls=1,gpu_seconds=1,
                              cpu_seconds=1,wall_seconds=1))
        b = point("b", .7, v(tokens=3,test_calls=3,gpu_seconds=3,
                              cpu_seconds=3,wall_seconds=3))
        x = audit_resource_quality_frontier((a,b), UNIT_CAP, 1)
        self.assertEqual(x.nondominated_policies, ("a",))
        self.assertAlmostEqual(x.exact_normalized_hypervolume, .9*.9**5)
        self.assertNotEqual(x.exact_normalized_hypervolume,
                            (.9*.9**5) + (.7*.7**5))

    def test_float_nan_inf_negative_and_boolean_quality_rejected(self):
        for score in (float("nan"),float("inf"),-0.1,1.1,True,False,"0.5"):
            with self.subTest(score=score), self.assertRaises(ValueError):
                point("a",score,USED_A)
        with self.assertRaisesRegex(TypeError, "ResourceVector"):
            point("a",.5, {"tokens":1})

    def test_malformed_policy_duplicate_and_more_than_eight_rejected(self):
        with self.assertRaisesRegex(ValueError, "policy ID"):
            point("",.5,USED_A)
        with self.assertRaisesRegex(ValueError, "duplicate policy"):
            audit_resource_quality_frontier(
                (point("same",.4,USED_A),point("same",.6,USED_B)),
                UNIT_CAP,1)
        with self.assertRaisesRegex(ValueError, "one to eight"):
            audit_resource_quality_frontier(
                tuple(point(f"arm-{i}",.5,USED_A)
                      for i in range(MAX_PARETO_POLICIES+1)),
                UNIT_CAP,1)

    def test_boolean_nonpositive_assignment_and_invalid_sequences(self):
        for count in (0,-1,True,1.5):
            with self.subTest(count=count), self.assertRaises(ValueError):
                audit_resource_quality_frontier(
                    (point("a",.5,USED_A),), UNIT_CAP, count)
        with self.assertRaises(TypeError):
            audit_resource_quality_frontier("a,b",UNIT_CAP,1)
        with self.assertRaises(TypeError):
            dominates("a",point("b",.5,USED_A))

    def test_independent_subset_union_reference_for_random_3_point_cases(self):
        rng = Random(20261109)
        for trial in range(30):
            arms=[]
            for i in range(rng.randrange(2,5)):
                cost = RV(**{
                    k: rng.randrange(0,11)
                    for k in RESOURCE_FIELDS
                })
                quality = rng.randrange(0,11) / 10
                arms.append(point(f"arm-{i}",quality,cost))
            x=audit_resource_quality_frontier(tuple(arms),UNIT_CAP,1)
            independent=independent_inclusion_exclusion_hv(arms,UNIT_CAP)
            with self.subTest(trial=trial):
                self.assertAlmostEqual(x.exact_normalized_hypervolume,
                                       independent,places=12)
                self.assertTrue(0<=x.exact_normalized_hypervolume<=1)

    def test_marginal_contributions_nonnegative_and_bounded(self):
        arms=(point("a",.6,USED_A),point("b",.85,USED_B),
              point("c",.4,v(tokens=4,test_calls=1,gpu_seconds=7,
                               cpu_seconds=1,wall_seconds=5)))
        x=audit_resource_quality_frontier(arms,UNIT_CAP,1)
        for name,contribution in x.marginal_hypervolume_by_policy:
            self.assertTrue(0<=contribution<=x.exact_normalized_hypervolume)

    def test_permutation_invariance_of_frontier_ties_and_hypervolume(self):
        arms=(point("z",.8,USED_A),point("a",.6,USED_B),
              point("b",.8,USED_A),point("k",.9,v(tokens=5,
                    test_calls=1,gpu_seconds=7,cpu_seconds=1,wall_seconds=3)))
        a=audit_resource_quality_frontier(arms,UNIT_CAP,1)
        b=audit_resource_quality_frontier(tuple(reversed(arms)),UNIT_CAP,1)
        self.assertEqual(asdict(a),asdict(b))

    def test_study_audit_matches_full_task_denominators_and_cost_totals(self):
        study,records,gold=synthetic_matrix()
        report=audit_synthetic(study,records,gold)
        self.assertEqual(report.matched_assignments_per_policy,2)
        self.assertEqual(report.model_id,"fake-model")
        self.assertEqual(report.budget_id,"fake-budget")
        self.assertEqual(report.nondominated_policies,("treatment",))
        arms={a.policy:a for a in report.arms}
        self.assertEqual(arms["treatment"].evaluator_claimed_success_rate,1.)
        self.assertEqual(arms["baseline"].evaluator_claimed_success_rate,.5)
        self.assertEqual(arms["treatment"].total_reported_cost.tokens,3)
        self.assertEqual(arms["baseline"].total_reported_cost.tokens,4)
        self.assertAlmostEqual(
            report.exact_normalized_hypervolume,
            (1 - 3/20) * (1 - 3/20) * (1 - 2/20)**3,
        )
        self.assertFalse(report.real_experiment_approved)

    def test_unqualified_model_budget_id_rejected(self):
        study,records,gold=synthetic_matrix()
        with self.assertRaisesRegex(ValueError,"frozen experimental factors"):
            audit_matched_postterminal_pareto(
                study,records,gold,model_id="phantom",budget_id="fake-budget")
        with self.assertRaisesRegex(ValueError,"frozen experimental factors"):
            audit_matched_postterminal_pareto(
                study,records,gold,model_id="fake-model",budget_id="other")

    def test_infrastructure_failure_suppresses_quality_hypervolume(self):
        study,records,gold=synthetic_matrix(state="infra")
        with self.assertRaisesRegex(ValueError,"incomplete"):
            audit_synthetic(study,records,gold)

    def test_timeout_safety_suppresses_quality_hypervolume(self):
        study,records,gold=synthetic_matrix(state="timeout")
        with self.assertRaisesRegex(ValueError,"incomplete"):
            audit_synthetic(study,records,gold)

    def test_missing_oracle_cannot_be_inferred_from_cost(self):
        study,records,gold=synthetic_matrix()
        with self.assertRaisesRegex(ValueError,"lacks"):
            audit_synthetic(study,records,gold[:-1])

    def test_bad_patch_hash_never_joins_for_favorable_success(self):
        study,records,gold=synthetic_matrix()
        changed=(replace(gold[0],patch_sha256="1"*64),)+gold[1:]
        with self.assertRaisesRegex(ValueError,"different from released"):
            audit_synthetic(study,records,changed)

    def test_mismatched_checkpoint_across_policies_rejected(self):
        study,records,gold=synthetic_matrix()
        changed=(replace(records[0],model_checkpoint_sha40="f"*40),)+records[1:]
        with self.assertRaisesRegex(ValueError,"model checkpoint"):
            audit_synthetic(study,changed,gold)

    def test_missing_pair_cell_never_shrinks_denominator(self):
        study,records,gold=synthetic_matrix()
        with self.assertRaisesRegex(ValueError,"incomplete"):
            audit_synthetic(study,records[:-1],gold)

    def test_each_of_five_resource_overruns_in_receipts_rejected(self):
        study,records,gold=synthetic_matrix()
        for field in RESOURCE_FIELDS:
            values={dim:getattr(records[0].consumed,dim) for dim in RESOURCE_FIELDS}
            values[field]=11 if field in ("tokens","test_calls") else 10.1
            modified=(replace(records[0],consumed=RV(**values)),)+records[1:]
            with self.subTest(dim=field), self.assertRaisesRegex(
                    ValueError,"FIVE-resource"):
                audit_synthetic(study,modified,gold)

    def test_released_patch_not_counted_if_no_oracle_evidence(self):
        study,records,gold=synthetic_matrix()
        deleted=tuple(v for v in gold if not (
            v.task_id=="fake-task-1" and v.policy=="baseline"))
        with self.assertRaisesRegex(ValueError,"lacks"):
            audit_synthetic(study,records,deleted)

    def test_report_never_contains_oracle_hash_or_model_proof(self):
        study,records,gold=synthetic_matrix()
        report=audit_synthetic(study,records,gold)
        body=json.dumps(asdict(report),sort_keys=True)
        self.assertNotIn("oracle_artifact_sha256",body)
        self.assertNotIn("evaluator_log_sha256",body)
        self.assertNotIn("patch_sha256",body)
        self.assertFalse(report.reported_costs_independently_measured)
        self.assertFalse(report.hidden_oracles_independently_authenticated)
        self.assertFalse(report.licensed_models_and_tasks_qualified)
        self.assertFalse(report.real_experiment_approved)
        self.assertIn("NOT_REAL_RESULTS",report.stage)


if __name__=="__main__":
    unittest.main()
