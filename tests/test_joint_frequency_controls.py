"""Synthetic-only validation of frozen train-only joint categorical controls.

All labels are constructed first-party toy observations, NOT independent
external correctness, security verification or real benchmark evidence.
"""
from dataclasses import replace
from hashlib import sha256
import math
import unittest

from ucode.acquisition import ParetoPoint
from ucode.diagnostic_fit import GroupPartitions
from ucode.joint_frequency_fit import (
    JointOutcomeLabel, fit_training_joint_frequency,
    validate_frozen_joint_frequency, FrozenJointFrequency,
)
from ucode.joint_frequency_controls import (
    JointForecastCandidate, compare_same_marginal_joint_controllers,
)
from ucode.vector_policy import ResourcePrices, ResourceVector


PARTS=GroupPartitions(
    frozenset(("train-1","train-2","train-3","train-4")),
    frozenset(("val-1","val-2")),
    frozenset(("never-eval-1",)),
)
CHECKPOINT=sha256(b"SYNTHETIC_MODEL_CHECKPOINT_NOT_REAL_WEIGHTS").hexdigest()
PRICES=ResourcePrices(tokens=.01)
CAP=ResourceVector(tokens=10,test_calls=2,gpu_seconds=10,
                   cpu_seconds=9,wall_seconds=8)


def row(i, group, atom=(0,0,0), *,
        context="PREOUTCOME_BUCKET_A",model="synthetic-model",
        checkpoint=CHECKPOINT, action="generate",
        protocol="synthetic-label-v1"):
    r,s,v=atom
    return JointOutcomeLabel(
        task_id="SYNTHETIC_TASK_%d"%i,
        lineage_group=group,
        proposal_id="SYNTHETIC_CANDIDATE_%d"%i,
        model_id=model,model_checkpoint_sha256=checkpoint,action=action,
        public_context_bucket=context,
        preoutcome_snapshot_sha256=sha256(
            ("SYNTHETIC_VISIBLE_%d"%i).encode()).hexdigest(),
        preoutcome_time=100+i,
        label_time=200+i,
        labeling_protocol_id=protocol,
        reliability_high=r,safety_high=s,candidate_valid=v,
        training_label_ref="SYNTHETIC_TRAINING_LABEL_%d"%i,
    )


def training_rows():
    # Each group has 4 atom-000 and 4 atom-111 observations. Strong
    # positive three-way dependence; all three marginal probabilities=.5.
    return [row(i,g,(0,0,0) if offset<4 else (1,1,1))
            for n,g in enumerate(sorted(PARTS.train))
            for offset in range(8) for i in (n*8+offset,)]


def validation_rows():
    return [row(100+i,g,(0,0,0) if offset<4 else (1,1,1))
            for n,g in enumerate(sorted(PARTS.validation))
            for offset in range(8) for i in (n*8+offset,)]


def fit(rows=None,parts=PARTS,**kw):
    return fit_training_joint_frequency(
        training_rows() if rows is None else rows,parts,
        "synthetic-model","generate","PREOUTCOME_BUCKET_A",
        "synthetic-label-v1",model_checkpoint_sha256=CHECKPOINT,**kw,
    )


class JointFrequencyTrainingTests(unittest.TestCase):
    def test_group_balanced_joint_model_marginals_and_mass(self):
        f=fit()
        self.assertEqual(f.training_task_count,32)
        self.assertEqual(f.training_lineage_count,4)
        self.assertEqual(f.status,
            "TRAIN_ONLY_SMOOTHED_CATEGORICAL_JOINT_NOT_ATTESTED_NOT_CALIBRATED")
        self.assertAlmostEqual(sum(f.masses),1.)
        self.assertEqual(len(f.masses),8)
        self.assertEqual(f.marginal_high(),(.5,.5,.5))
        self.assertGreater(f.masses[7],.3)
        self.assertLess(f.masses[1],.1)
        self.assertEqual(len(f.training_fingerprint_sha256),64)

    def test_input_order_determinism_and_fingerprint_sensitivity(self):
        rows=training_rows()
        self.assertEqual(fit(rows),fit(list(reversed(rows))))
        changed=rows.copy()
        changed[0]=replace(changed[0],training_label_ref="SYNTHETIC_OTHER")
        self.assertNotEqual(
            fit(changed).training_fingerprint_sha256,
            fit(rows).training_fingerprint_sha256,
        )

    def test_equal_lineage_weight_not_large_repository_domination(self):
        # Group 1 has 40 tasks (90% zero) versus group 2 with 10
        # (90% one). Correct *equal group* weight => high marginal .5.
        rows=[]
        for n in range(40):
            rows.append(row(n,"train-1",(0,0,0) if n<36 else (1,1,1)))
        for n in range(10):
            rows.append(row(100+n,"train-2",(0,0,0) if n==0 else (1,1,1)))
        f=fit(rows)
        self.assertAlmostEqual(f.marginal_high()[0],.5,places=12)
        self.assertEqual(f.training_lineage_count,2)
        # Naive per-candidate mean differs: only 13/50 high.
        self.assertAlmostEqual(13/50,.26)

    def test_validation_metrics_heldout_and_no_refit(self):
        f=fit()
        same=fit()
        r=validate_frozen_joint_frequency(f,validation_rows(),PARTS)
        self.assertEqual(f,same)
        self.assertEqual(r.validation_tasks,16)
        self.assertEqual(r.validation_lineages,2)
        self.assertEqual(r.marginal_absolute_calibration_error,(0.,0.,0.))
        self.assertAlmostEqual(r.marginal_brier_mean,.25,places=12)
        self.assertGreater(r.categorical_eight_class_brier,0.)
        self.assertGreater(r.categorical_log_loss,0.)
        self.assertIn("VALIDATION_DESCRIPTIVE",r.status)

    def test_evaluation_or_training_rows_refused_by_validation(self):
        f=fit()
        bad_eval=[replace(validation_rows()[0],lineage_group="never-eval-1")]
        with self.assertRaisesRegex(ValueError,"forbidden"):
            validate_frozen_joint_frequency(f,bad_eval,PARTS,
                                             minimum_validation_tasks=1)
        with self.assertRaisesRegex(ValueError,"forbidden"):
            validate_frozen_joint_frequency(f,training_rows(),PARTS)

    def test_training_rejects_validation_evaluation_and_unassigned(self):
        for g in ("val-1","never-eval-1","unassigned"):
            bad=training_rows()+[row(500,g,(0,0,0))]
            with self.subTest(g=g),self.assertRaises(ValueError):
                fit(bad)

    def test_cross_task_overlap_even_with_forged_different_lineage(self):
        f=fit()
        vr=validation_rows()
        vr[0]=replace(vr[0],task_id=training_rows()[0].task_id)
        with self.assertRaisesRegex(ValueError,"task overlap"):
            validate_frozen_joint_frequency(f,vr,PARTS)

    def test_mixed_model_action_context_or_label_protocol_refused(self):
        target=training_rows()
        for field,value in (
            ("model_id","other-model"),("action","repair"),
            ("public_context_bucket","POST_ORACLE_EVASION"),
            ("labeling_protocol_id","changed-protocol"),
        ):
            bad=target.copy()
            bad[0]=replace(bad[0],**{field:value})
            with self.subTest(field=field),self.assertRaisesRegex(
                ValueError,"mixing models"):
                fit(bad)

    def test_one_proposal_per_task_no_task_pseudoreplication(self):
        original=training_rows()
        duplicated=replace(original[0],proposal_id="another-proposal")
        with self.assertRaisesRegex(ValueError,"duplicate task"):
            fit(original+[duplicated])
        with self.assertRaisesRegex(ValueError,"duplicate task"):
            validate_frozen_joint_frequency(fit(),
                validation_rows()+[validation_rows()[0]],PARTS)

    def test_per_marginal_class_support_cannot_be_one_lineage(self):
        # Two independent lineages globally but every positive event
        # occurs exclusively in one; fitting must fail, not auto-smooth.
        rows=[row(i,"train-1",(0,0,0)) for i in range(8)]+[
            row(100+i,"train-2",(1,1,1)) for i in range(8)]
        with self.assertRaisesRegex(ValueError,"class-conditional"):
            fit(rows)

    def test_nonbinary_missing_label_bool_and_unordered_timestamps(self):
        base=training_rows()[0]
        for field,value in (
            ("reliability_high",True),("safety_high",None),
            ("candidate_valid",2),("candidate_valid",.0),
        ):
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"binary integer"):
                replace(base,**{field:value})
        for field,value in (
            ("preoutcome_time",base.label_time),
            ("label_time",base.preoutcome_time-1),
            ("preoutcome_time",True),
        ):
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"pre-outcome"):
                replace(base,**{field:value})
        with self.assertRaisesRegex(ValueError,"SHA256"):
            replace(base,preoutcome_snapshot_sha256="z"*64)

    def test_invalid_unsafe_pseudocount_and_lineage_threshold(self):
        for kw in (
            {"smoothing_per_atom":0},
            {"smoothing_per_atom":float("nan")},
            {"smoothing_per_atom":float("inf")},
            {"minimum_class_lineages":1},
            {"minimum_lineages":1},
        ):
            with self.subTest(kw=kw),self.assertRaises(ValueError):
                fit(**kw)

    def test_validation_requires_distinct_groups_and_min_rows(self):
        f=fit()
        only=[r for r in validation_rows() if r.lineage_group=="val-1"]
        with self.assertRaisesRegex(ValueError,"insufficient"):
            validate_frozen_joint_frequency(f,only,PARTS)
        with self.assertRaisesRegex(ValueError,"insufficient"):
            validate_frozen_joint_frequency(
                f,validation_rows()[:2],PARTS)

    def test_preoutcome_snapshot_and_training_label_are_not_public_output(self):
        f=fit()
        self.assertNotIn("training_label_ref",f.__dict__)
        self.assertNotIn("reliability_high",f.__dict__)
        self.assertNotIn("candidate_valid",f.__dict__)
        self.assertNotIn("preoutcome_snapshot_sha256",f.__dict__)
        self.assertNotIn("oracle",f.__dict__)
        self.assertNotIn("attested",f.status.lower().split("_")[-1])
        self.assertNotEqual(f.training_fingerprint_sha256,"a"*64)


class MatchedJointControllerTests(unittest.TestCase):
    def setUp(self):
        self.f=fit()
        self.risky=JointForecastCandidate(
            self.f.proposal(
                "risky", (0.,1.),(0.,1.),ResourceVector(tokens=1)),
            self.f)
        self.stable=JointForecastCandidate(
            self.f.proposal(
                "stable",(.5,.5),(.5,.5),ResourceVector(tokens=2)),
            self.f,
        )

    def compare(self,rows=None,cap=CAP):
        return compare_same_marginal_joint_controllers(
            (), (self.risky,self.stable) if rows is None else rows,
            cap, PRICES,
        )

    def test_all_four_receive_identical_marginals_and_costs(self):
        r=self.compare()
        self.assertEqual(r.eligible_candidate_count,2)
        self.assertEqual(r.source_model_id,"synthetic-model")
        self.assertEqual(r.source_labeling_protocol_id,"synthetic-label-v1")
        self.assertEqual({x.action_id for x in r.candidate_scores},{"risky","stable"})
        byid={x.action_id:x for x in r.candidate_scores}
        self.assertAlmostEqual(byid["risky"].gross_joint_expected,
                               self.f.masses[7],places=12)
        self.assertAlmostEqual(byid["risky"].gross_three_way_lower,0.,places=12)
        self.assertLessEqual(byid["risky"].gross_three_way_lower,
                             byid["risky"].gross_joint_expected)
        self.assertLessEqual(byid["risky"].gross_joint_expected,
                             byid["risky"].gross_three_way_upper)
        self.assertAlmostEqual(byid["stable"].gross_joint_expected,.125,places=12)
        self.assertEqual(self.risky.proposal.probability_valid,.5)

    def test_fitted_joint_winner_vs_robust_winner(self):
        choices=dict(self.compare().choices)
        self.assertEqual(
            choices["train_only_joint_frequency_expected"],"risky")
        self.assertEqual(
            choices["three_way_dependence_robust"],"stable")
        self.assertEqual(
            choices["two_way_dependence_robust_independent_validity"],"stable")
        self.assertEqual(
            choices["fully_independent_expected"],"risky")

    def test_permutation_invariance_and_reproducibility(self):
        a=self.compare()
        b=self.compare((self.stable,self.risky))
        self.assertEqual(a,b)
        self.assertIn("SOURCE_ONLY",a.status)

    def test_same_budget_five_vector_enforced_for_every_policy(self):
        for field in ("tokens","test_calls","gpu_seconds",
                      "cpu_seconds","wall_seconds"):
            cap=replace(CAP,**{field:0})
            bad_cost=ResourceVector(**{field:1})
            p=self.f.proposal("only",(.0,1.),(.0,1.),bad_cost)
            result=self.compare((JointForecastCandidate(p,self.f),),cap)
            with self.subTest(field=field):
                self.assertEqual(result.eligible_candidate_count,0)
                self.assertTrue(all(choice is None for _,choice in result.choices))

    def test_unmatched_marginals_do_not_allow_unfair_comparison(self):
        wrong=replace(
            self.risky.proposal,
            reliability=replace(self.risky.proposal.reliability,
                                probability_high=.9))
        with self.assertRaisesRegex(ValueError,"marginal mismatch"):
            self.compare((JointForecastCandidate(wrong,self.f),))

    def test_mixed_model_or_protocol_never_pool_in_one_comparison(self):
        changed_model=replace(self.f,model_id="new-model")
        changed_protocol=replace(self.f,labeling_protocol_id="new-protocol")
        for f in (changed_model,changed_protocol):
            with self.subTest(f=f),self.assertRaisesRegex(
                    ValueError,"cross-model or cross-label-protocol"):
                self.compare((self.risky,
                    JointForecastCandidate(
                        f.proposal("other",(.0,1.),(.0,1.),
                                   ResourceVector(tokens=1)),f)))

    def test_mismatched_action_refused(self):
        wrong=replace(self.f,action="repair")
        with self.assertRaisesRegex(ValueError,"forecast action"):
            self.compare((JointForecastCandidate(
                self.risky.proposal,wrong),))

    def test_duplicate_action_and_empty_menu_fails(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.compare((self.risky,self.risky))
        with self.assertRaisesRegex(ValueError,"nonempty"):
            self.compare(())

    def test_no_score_if_above_all_resources_and_stop_respects_zero(self):
        cap=ResourceVector()
        r=self.compare(cap=cap)
        self.assertEqual(r.eligible_candidate_count,0)
        self.assertTrue(all(choice is None for _,choice in r.choices))
        self.assertEqual(r.shared_resource_budget,cap)

    def test_deterministic_lexical_equal_scores(self):
        # Positive HVI for *every* policy: both candidates have fixed
        # R/S=.5, validity=.5, cost=.01. No robust STOP confound.
        a=self.f.proposal("a",(.5,.5),(.5,.5),ResourceVector(tokens=1))
        b=self.f.proposal("b",(.5,.5),(.5,.5),ResourceVector(tokens=1))
        r=self.compare((JointForecastCandidate(b,self.f),
                        JointForecastCandidate(a,self.f)))
        self.assertTrue(all(x=="a" for _,x in r.choices))

    def test_fitted_forecast_cannot_be_pretend_empirical_result(self):
        f=self.f
        self.assertIn("NOT_ATTESTED",f.status)
        self.assertEqual(len(f.training_task_hashes),32)
        r=self.compare()
        self.assertNotIn("success_rate",r.__dict__)
        self.assertNotIn("independent_oracle",r.__dict__)
        self.assertNotIn("real_code",r.__dict__)


if __name__=="__main__":
    unittest.main()
