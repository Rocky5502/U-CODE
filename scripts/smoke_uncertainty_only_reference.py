"""First-party offline confidence-only ablation; no real task or oracle.

The public test sign is deliberately synthetic. No calibration fit, model
inference, trusted metering, or empirical software correctness is possible.
"""
import json

from ucode.action_id_replay_bridge import ActionBoundBook, ActionBoundResponse
from ucode.adaptive_reference_replay import run_adaptive_synthetic_reference
from ucode.uncertainty_only_reference import SyntheticConfidenceCard, SyntheticRiskRegister
from ucode.optimized_search import SearchAction
from ucode.vector_policy import ResourceVector as RV


def main():
    sha="a"*64
    gen=SearchAction("generate-1","generate",RV(tokens=5))
    test=SearchAction("test-1","test",RV(test_calls=1))
    cap=RV(tokens=10,test_calls=2,gpu_seconds=1,cpu_seconds=2,wall_seconds=5)
    def book(positive):
        return ActionBoundBook((gen,test),(
            ActionBoundResponse(gen.action_id,"generate",None,gen.cost,RV(tokens=4),
                                produced_sha256=sha),
            ActionBoundResponse(test.action_id,"test",sha,test.cost,test.cost,
                                visible_positive=positive),
        ))
    config=SyntheticRiskRegister(
        (SyntheticConfidenceCard(sha,0.5,0.95,0.95),),
        release_min_probability=0.9)
    results={}
    for label,positive in (("synthetic_positive_test",True),
                           ("synthetic_negative_test",False)):
        x=run_adaptive_synthetic_reference(
            "SYNTHETIC_CONFIDENCE_ONLY","uncertainty_only",cap,
            book(positive),uncertainty_register=config)
        results[label]={
            "selected_public_action_ids":x.selected_action_ids,
            "status":x.status,
            "independent_oracle_results":x.independent_oracle_labels,
            "model_calls":x.model_inferences,
            "trusted_meter":x.trusted_resource_meter,
        }
    print(json.dumps({
        "scope":"SYNTHETIC_ONLY_UNCALIBRATED_ASSUMED_CONFIDENCE",
        "baseline":"uncertainty_only_LOCAL_REFERENCE_NOT_FAITHFUL_PUBLISHED_POLICY",
        "same_assumed_prior":0.5,
        "same_assumed_test_sensitivity":0.95,
        "same_assumed_test_specificity":0.95,
        "different_fabricated_public_test_sign":True,
        "records":results,
        "real_task_outcomes":0,
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
