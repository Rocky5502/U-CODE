"""Postterminal metrics with deliberately synthetic receipts; no real results."""
from dataclasses import replace
import unittest

from ucode.experiment_contract import (
    EvaluatorVerdict, FrozenStudy, PolicyRunReceipt,
)
from ucode.postterminal_accounting import postterminal_contrast
from ucode.vector_policy import ResourceVector as RV

CAP=RV(tokens=50,test_calls=3,gpu_seconds=1,cpu_seconds=10,wall_seconds=20)
LOG="a"*64
PATCH="b"*64


def sample():
    study=FrozenStudy(
        (("t1","lineage-A"),("t2","lineage-B")),
        ("fake-model",),("ucode","baseline"),(11,),
        (("pilot",CAP),),
    )
    statuses={
        ("t1","ucode"):("release",True),
        ("t1","baseline"):("infrastructure_failure",None),
        ("t2","ucode"):("timeout",None),
        ("t2","baseline"):("release",True),
    }
    receipts=[]
    verdicts=[]
    for task,group in study.task_lineages:
        for policy in study.policies:
            term,gold=statuses[(task,policy)]
            receipt=PolicyRunReceipt(
                task,group,"fake-model",policy,11,"pilot",
                "c"*40,"d"*40,"e"*64,"f"*64,
                RV(tokens=21 if policy=="ucode" else 10,
                   test_calls=2 if policy=="ucode" else 1,
                   gpu_seconds=0.5,cpu_seconds=3,wall_seconds=6),
                term,PATCH if term=="release" else None,LOG,
            )
            receipts.append(receipt)
            if term=="release":
                verdicts.append(EvaluatorVerdict(
                    task,"fake-model",policy,11,"pilot",PATCH,
                    "0"*64,gold,"1"*64,
                ))
    return study,tuple(receipts),tuple(verdicts)


class PostterminalAccountingTests(unittest.TestCase):
    def setUp(self):
        self.study,self.runs,self.verdicts=sample()

    def account(self,receipts=None,verdicts=None,study=None,**kwargs):
        return postterminal_contrast(
            self.study if study is None else study,
            self.runs if receipts is None else receipts,
            self.verdicts if verdicts is None else verdicts,
            "ucode","baseline",**kwargs)

    def test_infra_unknown_retained_not_deleted_from_primary_denominator(self):
        x=self.account()
        self.assertEqual(x.assigned_pairs,2)
        self.assertEqual(x.treatment.assigned,2)
        self.assertEqual(x.control.assigned,2)
        self.assertEqual(x.treatment.verified_successes,1)
        self.assertEqual(x.treatment.timeouts,1)
        self.assertEqual(x.control.infrastructure_failures,1)
        self.assertEqual(x.treatment.full_task_success_bounds,(0.5,0.5))
        self.assertEqual(x.control.full_task_success_bounds,(0.5,1.0))
        self.assertEqual(x.paired_success_bounds.lower_effect,-0.5)
        self.assertEqual(x.paired_success_bounds.upper_effect,0.0)
        self.assertIsNone(x.paired_complete_case_estimate)
        self.assertFalse(x.real_trial_approved)

    def test_release_coverage_bounds_and_wrong_release_risk(self):
        x=self.account()
        self.assertEqual(x.treatment.release_coverage_bounds,(0.5,0.5))
        self.assertEqual(x.control.release_coverage_bounds,(0.5,1.0))
        self.assertEqual(x.treatment.observed_wrong_release_risk,0)
        self.assertEqual(x.control.wrong_release_risk_bounds,(0,0.5))
        self.assertEqual(x.control.releases_with_verdict,1)
        self.assertEqual(x.control.known_wrong_releases,0)
        self.assertFalse(x.control.independently_authenticated_oracle)

    def test_fractional_mean_token_and_test_count_supported(self):
        receipts=list(self.runs)
        target=receipts[0]
        receipts[0]=replace(target,consumed=RV(
            tokens=20,test_calls=1,gpu_seconds=.3,cpu_seconds=3,wall_seconds=6))
        x=self.account(receipts=tuple(receipts))
        m=dict(x.treatment.mean_reported_cost_per_assignment)
        self.assertEqual(m["tokens"],20.5)
        self.assertEqual(m["test_calls"],1.5)
        self.assertAlmostEqual(m["gpu_seconds"],.4)
        self.assertFalse(x.treatment.authenticated_meter)

    def test_failure_reason_accounting_has_no_undefined_gold_on_nonrelease(self):
        x=self.account()
        self.assertEqual(x.treatment.abstentions,0)
        self.assertEqual(x.treatment.safety_blocks,0)
        self.assertEqual(x.treatment.timeouts,1)
        self.assertEqual(x.control.infrastructure_failures,1)

    def test_wrong_release_has_distinct_risk_bounds(self):
        gold=list(self.verdicts)
        b=next(i for i,v in enumerate(gold) if v.policy=="baseline")
        gold[b]=replace(gold[b],oracle_passed=False)
        x=self.account(verdicts=tuple(gold))
        self.assertEqual(x.control.known_wrong_releases,1)
        self.assertEqual(x.control.observed_wrong_release_risk,1.0)
        self.assertEqual(x.control.wrong_release_risk_bounds,(.5,1.0))
        self.assertEqual(x.control.full_task_success_bounds,(0,.5))
        self.assertEqual(x.paired_success_bounds.lower_effect,0.0)
        self.assertEqual(x.paired_success_bounds.upper_effect,.5)

    def test_all_abstain_has_undefined_risk_not_zero(self):
        receipt=tuple(replace(r,termination="abstain",patch_sha256=None)
                      for r in self.runs)
        x=self.account(receipts=receipt,verdicts=())
        self.assertIsNone(x.treatment.observed_wrong_release_risk)
        self.assertIsNone(x.control.observed_wrong_release_risk)
        self.assertIsNone(x.treatment.wrong_release_risk_bounds)
        self.assertIsNone(x.control.wrong_release_risk_bounds)
        self.assertEqual(x.treatment.full_task_success_bounds,(0,0))
        self.assertEqual(x.treatment.release_coverage_bounds,(0,0))
        self.assertEqual(x.paired_complete_case_estimate.effect_success_difference,0)

    def test_zero_releases_but_unknown_infrastructure_has_uncertain_risk(self):
        modified=tuple(
            replace(r,termination="abstain",patch_sha256=None)
            if r.termination in ("release","timeout") else r
            for r in self.runs
        )
        x=self.account(receipts=modified,verdicts=())
        self.assertIsNone(x.control.observed_wrong_release_risk)
        self.assertEqual(x.control.wrong_release_risk_bounds,(0,1))
        self.assertEqual(x.control.release_coverage_bounds,(0,.5))

    def test_all_complete_terminal_runs_use_cluster_bootstrap(self):
        runs=tuple(replace(r,termination="abstain")
                   if r.termination in ("timeout","infrastructure_failure")
                   else r for r in self.runs)
        x=self.account(receipts=runs,bootstrap_samples=80,seed=12)
        self.assertIsNotNone(x.paired_complete_case_estimate)
        self.assertEqual(x.paired_complete_case_estimate.pairs,2)
        self.assertEqual(x.paired_success_bounds.lower_effect,
                         x.paired_success_bounds.upper_effect)
        self.assertEqual(x.paired_complete_case_estimate.effect_success_difference,0)
        self.assertEqual(x.paired_complete_case_estimate.cluster_bootstrap_ci_95,(-1,1))

    def test_order_invariant_across_evaluator_receipts(self):
        x=self.account()
        y=self.account(receipts=tuple(reversed(self.runs)),
                       verdicts=tuple(reversed(self.verdicts)))
        self.assertEqual(x,y)

    def test_missing_release_verdict_fails(self):
        with self.assertRaisesRegex(ValueError,"lacks"):
            self.account(verdicts=self.verdicts[:-1])

    def test_wrong_oracle_patch_fails(self):
        verdicts=(replace(self.verdicts[0],patch_sha256="9"*64),)+self.verdicts[1:]
        with self.assertRaisesRegex(ValueError,"different from released"):
            self.account(verdicts=verdicts)

    def test_unassigned_extra_oracle_fails(self):
        other=replace(self.verdicts[0],task_id="unassigned")
        with self.assertRaisesRegex(ValueError,"unassigned"):
            self.account(verdicts=self.verdicts+(other,))

    def test_missing_pair_cell_fails_even_under_infra_missingness(self):
        with self.assertRaisesRegex(ValueError,"incomplete"):
            self.account(receipts=self.runs[:-1])

    def test_duplicate_assigned_cell_fails(self):
        with self.assertRaisesRegex(ValueError,"duplicated"):
            self.account(receipts=self.runs[:-1]+(self.runs[0],))

    def test_policy_mismatched_checkpoint_fails(self):
        runs=(replace(self.runs[0],model_checkpoint_sha40="9"*40),)+self.runs[1:]
        with self.assertRaisesRegex(ValueError,"model checkpoint"):
            self.account(receipts=runs)

    def test_postterminal_only_cannot_accept_model_oracle_secrets(self):
        with self.assertRaises(TypeError):
            self.account(oracle_gold_from_future=True)
        self.assertFalse(hasattr(self.account(),"run_agent"))

    def test_reject_non_registered_policy_or_fake_seed(self):
        with self.assertRaisesRegex(ValueError,"preregistered"):
            postterminal_contrast(self.study,self.runs,self.verdicts,
                                  "ucode","oracle-gold")
        with self.assertRaisesRegex(ValueError,"bootstrap"):
            self.account(bootstrap_samples=True)

    def test_not_a_statistical_or_runtime_attestation(self):
        x=self.account()
        self.assertIn("NOT_CONFIDENCE",x.treatment.interval_kind)
        self.assertEqual(x.paired_success_bounds.interval_kind,
                         "worst_best_case_partial_identification_not_confidence_interval")
        self.assertFalse(x.treatment.authenticated_meter)
        self.assertFalse(x.treatment.independently_authenticated_oracle)


if __name__=="__main__":
    unittest.main()
