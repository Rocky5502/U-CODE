"""Reproducible synthetic joint-frequency fit and same-marginal M4 controls.

First-party artificial labels ONLY. This program is an interface/logic smoke,
NOT a real model, calibrated forecast, security finding or repair result.
"""
import json
from hashlib import sha256

from ucode.diagnostic_fit import GroupPartitions
from ucode.joint_frequency_fit import (
    JointOutcomeLabel,fit_training_joint_frequency,
    validate_frozen_joint_frequency,
)
from ucode.joint_frequency_controls import (
    JointForecastCandidate,compare_same_marginal_joint_controllers,
)
from ucode.vector_policy import ResourcePrices,ResourceVector

SYNTHETIC_CHECKPOINT=sha256(
    b"SYNTHETIC_MODEL_CHECKPOINT_NOT_REAL_WEIGHTS").hexdigest()


def row(i, group, atom):
    return JointOutcomeLabel(
        task_id=f"SYNTHETIC_TASK_{i}",lineage_group=group,
        proposal_id=f"SYNTHETIC_CANDIDATE_{i}",
        model_id="synthetic_model_not_loaded",
        model_checkpoint_sha256=SYNTHETIC_CHECKPOINT,
        action="generate",
        public_context_bucket="SYNTHETIC_PREOUTCOME_BUCKET",
        preoutcome_snapshot_sha256=sha256(f"synthetic_{i}".encode()).hexdigest(),
        preoutcome_time=100+i,label_time=1000+i,
        labeling_protocol_id="SYNTHETIC_PROTOCOL",
        reliability_high=atom,safety_high=atom,candidate_valid=atom,
        training_label_ref=f"SYNTHETIC_LABEL_{i}",
    )


def demo():
    groups=GroupPartitions(
        frozenset(("train1","train2","train3","train4")),
        frozenset(("val1","val2")),
        frozenset(("never_test",)),
    )
    train=[row(8*j+i,g,0 if i<4 else 1)
           for j,g in enumerate(sorted(groups.train)) for i in range(8)]
    val=[row(100+8*j+i,g,0 if i<4 else 1)
         for j,g in enumerate(sorted(groups.validation)) for i in range(8)]
    joint=fit_training_joint_frequency(
        train,groups,"synthetic_model_not_loaded","generate",
        "SYNTHETIC_PREOUTCOME_BUCKET","SYNTHETIC_PROTOCOL",
        model_checkpoint_sha256=SYNTHETIC_CHECKPOINT,
    )
    validation=validate_frozen_joint_frequency(joint,val,groups)
    candidates=(
        JointForecastCandidate(joint.proposal(
            "risky",(0.,1.),(0.,1.),ResourceVector(tokens=1)),joint),
        JointForecastCandidate(joint.proposal(
            "stable",(.5,.5),(.5,.5),ResourceVector(tokens=2)),joint),
    )
    compared=compare_same_marginal_joint_controllers(
        (),candidates,ResourceVector(tokens=10),ResourcePrices(tokens=.01),
    )
    choices=dict(compared.choices)
    assert choices["train_only_joint_frequency_expected"]=="risky"
    assert choices["three_way_dependence_robust"]=="stable"
    assert validation.validation_tasks==16
    return {
        "stage":"SYNTHETIC_TRAIN_ONLY_FREQUENCY_FOUR_WAY_CONTROL_NOT_EVALUATION",
        "train_tasks_invented":len(train),
        "train_declared_lineages":len(groups.train),
        "model_checkpoint_identity_is_synthetic":True,
        "heldout_validation_tasks_invented":len(val),
        "heldout_validation_lineages":validation.validation_lineages,
        "predicted_marginal_probabilities":joint.marginal_high(),
        "eight_atom_joint_mass":joint.masses,
        "categorical_brier_synthetic_validation":validation.categorical_eight_class_brier,
        "lineage_balanced_categorical_brier_synthetic_validation":
            validation.lineage_balanced_categorical_brier,
        "marginal_brier_synthetic_validation":validation.marginal_brier_mean,
        "policy_choices_on_matched_synthetic_candidates":choices,
        "registered_confirmatory_policy_arms_executed":0,
        "independently_qualified_real_tasks":0,
        "real_model_inference":0,
        "independent_hidden_oracle_evaluation":0,
        "measured_software_correctness_effect":None,
    }


if __name__=="__main__":
    print(json.dumps(demo(),sort_keys=True,indent=2))
