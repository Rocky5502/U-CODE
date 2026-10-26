"""Synthetic metering + immutable action-ledger adversarial tests.

No external repository code, user-controlled subprocesses or hidden oracles.
Only the fixed first-party subprocess fixture executes on Linux.
"""
from dataclasses import replace
from hashlib import sha256
import sys
import unittest

from ucode.matched_session import SharedDecision, SharedSession, commit_shared
from ucode.metering_attestation import (
    RESOURCE_FIELDS, SOURCE_BY_RESOURCE, MeterReading,
    MeteringAttestationError, check_five_resource_evidence,
    run_first_party_smoke,
)
from ucode.metering_reconciliation import reconcile_metering_action
from ucode.optimized_search import SearchAction
from ucode.vector_policy import ResourceVector

A = "a"*64
BUDGET = ResourceVector(tokens=10, test_calls=2, gpu_seconds=3,
                        cpu_seconds=4, wall_seconds=5)
GEN = SearchAction("gen", "generate", ResourceVector(tokens=1))
GEN2 = SearchAction("gen2", "generate", ResourceVector(tokens=1))
TEST = SearchAction("test", "test", ResourceVector(test_calls=1))


def matrix(cost=None, caps=None):
    cost = cost if cost is not None else ResourceVector(tokens=2)
    caps = caps or {
        "tokens": 10, "test_calls": 2,
        "gpu_seconds": 3, "cpu_seconds": 4, "wall_seconds": 5,
    }
    values = {name: getattr(cost, name) for name in RESOURCE_FIELDS}
    readings = {
        field: MeterReading(values[field], SOURCE_BY_RESOURCE[field],
                            sha256(("fixture:"+field).encode()).hexdigest(),
                            True, True)
        for field in RESOURCE_FIELDS
    }
    return caps, readings


def session_pair():
    before = SharedSession.empty(BUDGET)
    after = commit_shared(
        before, (GEN,), SharedDecision("gen", "generate", None, GEN.cost),
        reported_cost=ResourceVector(tokens=2), new_candidate_sha256=A,
    )
    return before, after


class StructuralMeterTests(unittest.TestCase):
    def test_complete_five_vector_structural_evidence(self):
        caps, readings = matrix()
        audit = check_five_resource_evidence("synthetic-001", caps, readings)
        self.assertEqual(tuple(k for k, _ in audit.consumed), RESOURCE_FIELDS)
        self.assertTrue(audit.structural_checks_passed)
        self.assertFalse(audit.externally_verified)
        self.assertFalse(audit.real_trial_approved)

    def test_missing_any_resource_fails_including_zero(self):
        for field in RESOURCE_FIELDS:
            with self.subTest(field=field):
                caps, readings = matrix()
                readings.pop(field)
                with self.assertRaisesRegex(MeteringAttestationError,
                                            "five separately"):
                    check_five_resource_evidence("run", caps, readings)

    def test_missing_cap_fails(self):
        caps, readings = matrix()
        caps.pop("gpu_seconds")
        with self.assertRaisesRegex(MeteringAttestationError,
                                    "five-component cap"):
            check_five_resource_evidence("run", caps, readings)

    def test_unexpected_resource_fails(self):
        caps, readings = matrix()
        readings["monetary_cost"] = readings["tokens"]
        with self.assertRaisesRegex(MeteringAttestationError, "five separately"):
            check_five_resource_evidence("run", caps, readings)

    def test_wrong_source_each_dimension_fails(self):
        for field in RESOURCE_FIELDS:
            with self.subTest(field=field):
                caps, readings = matrix()
                readings[field] = replace(readings[field], source="model-self-report")
                with self.assertRaisesRegex(MeteringAttestationError, "source"):
                    check_five_resource_evidence("run", caps, readings)

    def test_no_independence_claim_fails(self):
        caps, readings = matrix()
        readings["tokens"] = replace(readings["tokens"],
                                     independent_of_policy=False)
        with self.assertRaisesRegex(MeteringAttestationError, "independently"):
            check_five_resource_evidence("run", caps, readings)

    def test_no_enforcement_claim_fails(self):
        caps, readings = matrix()
        readings["wall_seconds"] = replace(readings["wall_seconds"],
                                           cap_enforced=False)
        with self.assertRaisesRegex(MeteringAttestationError, "enforced"):
            check_five_resource_evidence("run", caps, readings)

    def test_boolean_cap_and_reading_rejected(self):
        for field in ("tokens", "gpu_seconds"):
            with self.subTest(field=field):
                caps, readings = matrix()
                caps[field] = True
                with self.assertRaisesRegex(MeteringAttestationError, "invalid"):
                    check_five_resource_evidence("run", caps, readings)
                caps, readings = matrix()
                readings[field] = replace(readings[field], amount=True)
                with self.assertRaisesRegex(MeteringAttestationError, "invalid"):
                    check_five_resource_evidence("run", caps, readings)

    def test_negative_nan_infinite_readings_rejected(self):
        for value in (-1, float("nan"), float("inf")):
            with self.subTest(value=value):
                caps, readings = matrix()
                readings["wall_seconds"] = replace(
                    readings["wall_seconds"], amount=value)
                with self.assertRaisesRegex(MeteringAttestationError, "invalid"):
                    check_five_resource_evidence("run", caps, readings)

    def test_fractional_token_or_test_rejected(self):
        for field in ("tokens", "test_calls"):
            with self.subTest(field=field):
                caps, readings = matrix()
                readings[field] = replace(readings[field], amount=.5)
                with self.assertRaisesRegex(MeteringAttestationError, "invalid"):
                    check_five_resource_evidence("run", caps, readings)

    def test_zero_resource_still_requires_meter_source(self):
        caps, readings = matrix()
        self.assertEqual(readings["gpu_seconds"].amount, 0)
        readings["gpu_seconds"] = replace(readings["gpu_seconds"], source="")
        with self.assertRaisesRegex(MeteringAttestationError, "source"):
            check_five_resource_evidence("run", caps, readings)

    def test_individual_five_cap_breaches_fail(self):
        for field in RESOURCE_FIELDS:
            with self.subTest(field=field):
                caps, readings = matrix()
                value = caps[field]+1
                readings[field] = replace(readings[field], amount=value)
                with self.assertRaisesRegex(MeteringAttestationError, "exceeds"):
                    check_five_resource_evidence("run", caps, readings)

    def test_bad_meter_receipt_fingerprint_fails(self):
        caps, readings = matrix()
        readings["tokens"] = replace(readings["tokens"], receipt_sha256="000")
        with self.assertRaisesRegex(MeteringAttestationError, "SHA256"):
            check_five_resource_evidence("run", caps, readings)

    def test_run_id_validation(self):
        caps, readings = matrix()
        for bad in ("", " ", "x"*129, 42):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(MeteringAttestationError, "run identifier"):
                    check_five_resource_evidence(bad, caps, readings)


class MeteringLedgerTests(unittest.TestCase):
    def test_reconcile_one_exact_append(self):
        before, after = session_pair()
        caps, readings = matrix()
        proof = check_five_resource_evidence("test-run", caps, readings)
        bound = reconcile_metering_action(before, after, proof)
        self.assertEqual(bound.action_id, "gen")
        self.assertEqual(bound.consumed.tokens, 2)
        self.assertEqual(bound.before_trace_sha256, before.trace_sha256)
        self.assertEqual(bound.after_trace_sha256, after.trace_sha256)
        self.assertFalse(bound.independently_authenticated)
        self.assertFalse(bound.physical_caps_verified)
        self.assertFalse(bound.approved_real_trial)

    def test_audit_only_not_real_signoff(self):
        before, after = session_pair()
        caps, readings = matrix()
        proof = check_five_resource_evidence("run", caps, readings)
        for field in ("externally_verified", "real_trial_approved"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(MeteringAttestationError,
                                            "cannot certify"):
                    reconcile_metering_action(before, after,
                        replace(proof, **{field:True}))

    def test_forged_false_structural_check_refused(self):
        before, after = session_pair()
        caps, readings = matrix()
        proof = check_five_resource_evidence("run", caps, readings)
        with self.assertRaisesRegex(MeteringAttestationError, "cannot certify"):
            reconcile_metering_action(before, after,
                replace(proof, structural_checks_passed=False))

    def test_reported_tokens_disagree_with_meter(self):
        before, after = session_pair()
        caps, readings = matrix(ResourceVector(tokens=1))
        proof = check_five_resource_evidence("run", caps, readings)
        with self.assertRaisesRegex(MeteringAttestationError, "mismatch"):
            reconcile_metering_action(before, after, proof)

    def test_reported_non_token_dimension_disagreement(self):
        before, after = session_pair()
        for field in ("test_calls", "gpu_seconds", "cpu_seconds", "wall_seconds"):
            with self.subTest(field=field):
                caps, readings = matrix()
                readings[field] = replace(readings[field], amount=1)
                proof = check_five_resource_evidence("run", caps, readings)
                with self.assertRaisesRegex(MeteringAttestationError, "mismatch"):
                    reconcile_metering_action(before, after, proof)

    def test_same_session_not_one_append(self):
        before, after = session_pair()
        caps, readings = matrix()
        proof = check_five_resource_evidence("run", caps, readings)
        with self.assertRaisesRegex(MeteringAttestationError, "one appended"):
            reconcile_metering_action(before, before, proof)

    def test_two_appends_in_one_attestation_refused(self):
        before, after = session_pair()
        further = commit_shared(
            after, (GEN, GEN2),
            SharedDecision("gen2", "generate", None, GEN2.cost),
            reported_cost=GEN2.cost)
        caps, readings = matrix()
        proof = check_five_resource_evidence("run", caps, readings)
        with self.assertRaisesRegex(MeteringAttestationError, "one appended"):
            reconcile_metering_action(before, further, proof)

    def test_noncanonical_meter_order_fails(self):
        before, after = session_pair()
        caps, readings = matrix()
        proof = check_five_resource_evidence("run", caps, readings)
        with self.assertRaisesRegex(MeteringAttestationError, "canonical"):
            reconcile_metering_action(before, after, replace(
                proof, consumed=tuple(reversed(proof.consumed))))

    def test_missing_source_stamp_fails(self):
        before, after = session_pair()
        caps, readings = matrix()
        proof = check_five_resource_evidence("run", caps, readings)
        with self.assertRaisesRegex(MeteringAttestationError, "canonical"):
            reconcile_metering_action(before, after, replace(
                proof, source_fingerprints=proof.source_fingerprints[:-1]))

    def test_structural_evidence_is_not_cryptographic_proof(self):
        before, after = session_pair()
        caps, readings = matrix()
        proof = check_five_resource_evidence("run", caps, readings)
        # A digest-shaped *caller claim* can be substituted and still pass.
        # This asserts that no physical verification is claimed by our API.
        fake = replace(proof, source_fingerprints=tuple(
            (name, "f"*64) for name in RESOURCE_FIELDS))
        bound = reconcile_metering_action(before, after, fake)
        self.assertFalse(bound.independently_authenticated)
        self.assertFalse(bound.approved_real_trial)

    def test_ledger_contract_is_policy_neutral(self):
        self.assertFalse({"prior", "posterior", "oracle_passed", "hidden_tests"}
                         & set(type(reconcile_metering_action(*(
                             session_pair() + (check_five_resource_evidence(
                                 "run", *matrix()),)))).__dataclass_fields__))


@unittest.skipUnless(sys.platform == "linux",
                     "fixed first-party POSIX metering smoke is Linux-only")
class LinuxFirstPartySmokeTests(unittest.TestCase):
    def test_success_fixture(self):
        r = run_first_party_smoke("success", wall_limit_seconds=1.5)
        self.assertEqual(r.exit_code, 0)
        self.assertFalse(r.timed_out)
        self.assertGreaterEqual(r.wall_seconds, 0)
        self.assertGreaterEqual(r.cpu_seconds, 0)
        self.assertFalse(r.full_five_resource_trial_attested)
        self.assertFalse(r.network_isolation_enforced)

    def test_failure_fixture_not_mislabeled_success(self):
        r = run_first_party_smoke("failure", wall_limit_seconds=1.5)
        self.assertEqual(r.exit_code, 7)
        self.assertFalse(r.timed_out)

    def test_timeout_is_actually_killed(self):
        r = run_first_party_smoke("sleep", wall_limit_seconds=.2)
        self.assertTrue(r.timed_out)
        self.assertNotEqual(r.exit_code, 0)

    def test_no_arbitrary_fixture_execution(self):
        with self.assertRaisesRegex(ValueError, "predefined"):
            run_first_party_smoke("import os; print(os.listdir('/'))")

    def test_invalid_limits_rejected(self):
        for bad in (0, -1, float("nan"), 11, True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    run_first_party_smoke("success", wall_limit_seconds=bad)
        for bad in (0, 11, .5, True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    run_first_party_smoke("success", cpu_hard_limit_seconds=bad)


if __name__ == "__main__":
    unittest.main()
