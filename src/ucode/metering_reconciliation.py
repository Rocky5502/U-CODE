"""Policy-neutral STRUCTURAL reconciliation of metering evidence to U-CODE actions.

Never accepts self-reported model costs as independently measured telemetry.
Checks that a separately supplied *structural* metering audit describes the
same action receipt, five-vector delta, and immutable public trace as the
shared execution ledger. No secrets, oracle outcome, network access or code
execution; this is NOT a cryptographic attestation or hard-cap enforcer.

The caller CAN forge both objects. A separate privileged runner, signed
measurement evidence, enforcement during execution and independent reviewer
are prerequisites before reporting a measured confirmatory experiment.
"""
from dataclasses import dataclass

from .matched_session import SharedSession
from .metering_attestation import (
    RESOURCE_FIELDS, StructuralMeteringAudit, MeteringAttestationError,
)
from .vector_policy import ResourceVector


@dataclass(frozen=True)
class MeteringLedgerBinding:
    run_id: str
    action_id: str
    before_trace_sha256: str
    after_trace_sha256: str
    consumed: ResourceVector
    source_fingerprints: tuple[tuple[str, str], ...]
    scope: str = "STRUCTURAL_PER_ACTION_INCLUDES_DECLARED_CONTROLLER_OVERHEAD_ONLY"
    independently_authenticated: bool = False
    physical_caps_verified: bool = False
    approved_real_trial: bool = False


def reconcile_metering_action(
    before: SharedSession,
    after: SharedSession,
    structural: StructuralMeteringAudit,
) -> MeteringLedgerBinding:
    """Fail closed unless one appended action exactly matches five readings.

    This function deliberately does not expose a `trusted=True` mode.
    A successful result verifies internal bookkeeping consistency ONLY.
    Source identity and cap-enforcement booleans are untrusted declarations
    until the experimental runner authenticates/enforces them.
    """
    if (not isinstance(before, SharedSession)
            or not isinstance(after, SharedSession)
            or not isinstance(structural, StructuralMeteringAudit)):
        raise TypeError("typed sessions and structural metering audit required")
    if (structural.structural_checks_passed is not True
            or structural.externally_verified is not False
            or structural.real_trial_approved is not False):
        raise MeteringAttestationError(
            "structural meter evidence cannot certify external approval")
    if (before.initial_budget != after.initial_budget
            or before.max_candidates != after.max_candidates):
        raise MeteringAttestationError("shared budget/archive contract changed")
    if (len(after.receipts) != len(before.receipts) + 1
            or after.receipts[:-1] != before.receipts):
        raise MeteringAttestationError("exactly one appended immutable receipt required")
    before_state, after_state = before.state, after.state
    if (after_state.attempted != before_state.attempted
            + (after.receipts[-1].action_id,)):
        raise MeteringAttestationError("receipt does not match attempted chronology")
    if (not isinstance(structural.run_id, str)
            or not structural.run_id.strip()):
        raise MeteringAttestationError("nonblank structural run ID required")
    read = structural.consumed
    stamps = structural.source_fingerprints
    if (not isinstance(read, tuple) or len(read) != 5
            or tuple(k for k, _ in read) != RESOURCE_FIELDS
            or not isinstance(stamps, tuple) or len(stamps) != 5
            or tuple(k for k, _ in stamps) != RESOURCE_FIELDS):
        raise MeteringAttestationError("five canonical meter rows required")
    expected = after.receipts[-1].reported_cost
    for name, amount in read:
        if (type(amount) is bool or not isinstance(amount, (int, float))
                or getattr(expected, name) != amount):
            raise MeteringAttestationError(
                "external meter/ledger resource mismatch: " + name)
    for name in RESOURCE_FIELDS:
        delta = (getattr(before_state.remaining, name)
                 - getattr(after_state.remaining, name))
        if abs(delta - getattr(expected, name)) > 1e-7:
            raise MeteringAttestationError("shared five-vector budget delta mismatch")
    # Bind the digest of every event, not just the most recent reported vector.
    return MeteringLedgerBinding(
        structural.run_id, after.receipts[-1].action_id,
        before.trace_sha256, after.trace_sha256,
        expected, stamps,
    )
