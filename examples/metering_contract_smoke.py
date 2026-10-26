"""First-party ONLY structural meter/ledger smoke; NO real trial or oracle."""
from hashlib import sha256

from ucode.matched_session import SharedDecision, SharedSession, commit_shared
from ucode.metering_attestation import (
    RESOURCE_FIELDS, SOURCE_BY_RESOURCE, MeterReading,
    check_five_resource_evidence, run_first_party_smoke,
)
from ucode.metering_reconciliation import reconcile_metering_action
from ucode.optimized_search import SearchAction
from ucode.vector_policy import ResourceVector


def main():
    initial = ResourceVector(tokens=10, test_calls=2, gpu_seconds=3,
                             cpu_seconds=4, wall_seconds=5)
    action = SearchAction("gen", "generate", ResourceVector(tokens=1))
    before = SharedSession.empty(initial)
    after = commit_shared(before, (action,),
                          SharedDecision("gen", "generate", None, action.cost),
                          reported_cost=ResourceVector(tokens=2),
                          new_candidate_sha256="a"*64)
    caps = {f: getattr(initial, f) for f in RESOURCE_FIELDS}
    consumed = {f: getattr(after.receipts[-1].reported_cost, f)
                for f in RESOURCE_FIELDS}
    # This fixture explicitly simulates all five meter sources.
    reading = {
        f: MeterReading(
            consumed[f], SOURCE_BY_RESOURCE[f],
            sha256(("SYNTHETIC_SOURCE:"+f).encode()).hexdigest(),
            True, True,
        ) for f in RESOURCE_FIELDS
    }
    audit = check_five_resource_evidence("synthetic-only", caps, reading)
    bound = reconcile_metering_action(before, after, audit)
    assert bound.after_trace_sha256 == after.trace_sha256
    assert not bound.approved_real_trial and not bound.independently_authenticated
    fixed = run_first_party_smoke("success", wall_limit_seconds=2)
    assert fixed.exit_code == 0 and not fixed.full_five_resource_trial_attested
    print("U-CODE STRUCTURAL METERING ONLY / NO REAL EXPERIMENT")
    print("shared_action:", bound.action_id)
    print("public_trace_sha256:", bound.after_trace_sha256)
    print("five_readings:", bound.consumed)
    print("fixed_first_party_exit:", fixed.exit_code)
    print("physical_caps_verified:", bound.physical_caps_verified)
    print("approved_real_trial:", bound.approved_real_trial)


if __name__ == "__main__":
    main()
