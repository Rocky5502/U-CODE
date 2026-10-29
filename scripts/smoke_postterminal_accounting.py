"""Deterministic SYNTHETIC postterminal missingness/coverage/risk smoke.

The 'oracle' observations below are fabricated fixtures. This script has
NO real task execution, signed evaluator, model call or independent meter.
"""
from dataclasses import asdict
import json

from ucode.experiment_contract import EvaluatorVerdict, FrozenStudy, PolicyRunReceipt
from ucode.postterminal_accounting import postterminal_contrast
from ucode.vector_policy import ResourceVector as RV


def main():
    study=FrozenStudy(
        (("fake-t1","fake-fork-A"),("fake-t2","fake-fork-B")),
        ("fake-model",),("ucode_conditional_bes","no_uncertainty_search"),
        (11,), (("fake-budget",RV(tokens=50,test_calls=5,
                                 gpu_seconds=3,cpu_seconds=10,wall_seconds=20)),),
    )
    status={
        ("fake-t1","ucode_conditional_bes"):("release",True),
        ("fake-t1","no_uncertainty_search"):("infrastructure_failure",None),
        ("fake-t2","ucode_conditional_bes"):("timeout",None),
        ("fake-t2","no_uncertainty_search"):("release",False),
    }
    receipts=[]
    verdicts=[]
    for task,group in study.task_lineages:
        for arm in study.policies:
            term,oracle=status[(task,arm)]
            rec=PolicyRunReceipt(
                task,group,"fake-model",arm,11,"fake-budget",
                "1"*40,"2"*40,"3"*64,"4"*64,
                RV(tokens=11,test_calls=1,gpu_seconds=.1,
                   cpu_seconds=2,wall_seconds=3),
                term, "5"*64 if term=="release" else None,"6"*64,
            )
            receipts.append(rec)
            if term=="release":
                verdicts.append(EvaluatorVerdict(
                    task,"fake-model",arm,11,"fake-budget",
                    "5"*64,"7"*64,oracle,"8"*64))
    result=postterminal_contrast(
        study,tuple(receipts),tuple(verdicts),
        "ucode_conditional_bes","no_uncertainty_search",
        bootstrap_samples=100,seed=5,
    )
    if result.paired_complete_case_estimate is not None:
        raise AssertionError("unknown infrastructure outcome must suppress point estimate")
    if (result.paired_success_bounds.lower_effect!=0 or
            result.paired_success_bounds.upper_effect!=.5):
        raise AssertionError("missingness bounds changed without explanation")
    if result.control.observed_wrong_release_risk!=1.0:
        raise AssertionError("fixture release risk changed")
    print(json.dumps({
        "scope":"SYNTHETIC_POSTTERMINAL_ACCOUNTING_NOT_EMPIRICAL",
        "synthetic_fixture_assignments":len(receipts),
        "synthetic_fixture_evaluator_signs":len(verdicts),
        "real_task_executions":0,
        "real_independent_oracle_results":0,
        "authenticated_resource_meters":0,
        "independent_risk_certificates":0,
        "results":asdict(result),
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
