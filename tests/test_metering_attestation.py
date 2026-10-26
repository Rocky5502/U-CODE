"""Self-contained first-party SYNTHETIC structural metering tests."""
from dataclasses import replace
from hashlib import sha256
import sys
import unittest

from ucode.metering_attestation import (
    MeterReading, MeteringAttestationError, SOURCE_BY_RESOURCE,
    check_five_resource_evidence, run_first_party_smoke,
)


class MeteringContractTests(unittest.TestCase):
    def setUp(self):
        self.caps = {"tokens": 100, "test_calls": 2, "gpu_seconds": 3.5,
                     "cpu_seconds": 3.0, "wall_seconds": 4.0}
        self.readings = {
            f: MeterReading(0 if f in ("tokens", "test_calls") else 0.0,
                            source, sha256(f.encode()).hexdigest(), True, True)
            for f, source in SOURCE_BY_RESOURCE.items()
        }

    def validate(self, **kwargs):
        return check_five_resource_evidence("first-party-synthetic", self.caps,
                                            self.readings, **kwargs)

    def test_structural_shape_is_not_external_approval(self):
        a = self.validate()
        self.assertTrue(a.structural_checks_passed)
        self.assertFalse(a.externally_verified)
        self.assertFalse(a.real_trial_approved)
        self.assertEqual(len(a.consumed), 5)

    def test_missing_source_rejected_even_for_zero(self):
        for f in SOURCE_BY_RESOURCE:
            x = dict(self.readings)
            del x[f]
            with self.subTest(f=f), self.assertRaises(MeteringAttestationError):
                check_five_resource_evidence("x", self.caps, x)

    def test_each_enforcement_flag_required(self):
        for f in SOURCE_BY_RESOURCE:
            for replacement in (dict(cap_enforced=False),
                                dict(independent_of_policy=False)):
                x = dict(self.readings)
                x[f] = replace(x[f], **replacement)
                with self.subTest(f=f, replacement=replacement), self.assertRaisesRegex(
                        MeteringAttestationError, "independently metered"):
                    check_five_resource_evidence("x", self.caps, x)

    def test_model_reported_tokens_cannot_be_trusted_independent_meter(self):
        x = dict(self.readings)
        x["tokens"] = replace(x["tokens"], source="llm_self_report")
        with self.assertRaisesRegex(MeteringAttestationError, "self-reported"):
            check_five_resource_evidence("x", self.caps, x)

    def test_wrong_source_for_dimension(self):
        x = dict(self.readings)
        x["gpu_seconds"] = replace(x["gpu_seconds"], source="os_monotonic_clock")
        with self.assertRaises(MeteringAttestationError):
            check_five_resource_evidence("x", self.caps, x)

    def test_invalid_quantities_fail_closed(self):
        for number in (float("nan"), float("inf"), -1.0, True):
            x = dict(self.readings)
            x["cpu_seconds"] = replace(x["cpu_seconds"], amount=number)
            with self.subTest(value=number), self.assertRaises(MeteringAttestationError):
                check_five_resource_evidence("x", self.caps, x)
        x = dict(self.readings)
        x["test_calls"] = replace(x["test_calls"], amount=1.3)
        with self.assertRaises(MeteringAttestationError):
            check_five_resource_evidence("x", self.caps, x)

    def test_over_budget_even_if_signed_source_is_claimed(self):
        x = dict(self.readings)
        x["tokens"] = replace(x["tokens"], amount=101)
        with self.assertRaisesRegex(MeteringAttestationError, "exceeds"):
            check_five_resource_evidence("x", self.caps, x)

    def test_invalid_cap_and_missing_budget_fail_closed(self):
        for bad in (float("nan"), float("inf"), -1.0, True):
            caps = dict(self.caps)
            caps["wall_seconds"] = bad
            with self.subTest(value=bad), self.assertRaises(MeteringAttestationError):
                check_five_resource_evidence("x", caps, self.readings)
        caps = dict(self.caps)
        caps.pop("gpu_seconds")
        with self.assertRaises(MeteringAttestationError):
            check_five_resource_evidence("x", caps, self.readings)

    def test_invalid_proof_sha_and_run_identity(self):
        x = dict(self.readings)
        x["tokens"] = replace(x["tokens"], receipt_sha256="no digest")
        with self.assertRaises(MeteringAttestationError):
            check_five_resource_evidence("x", self.caps, x)
        with self.assertRaises(MeteringAttestationError):
            check_five_resource_evidence(" ", self.caps, self.readings)


@unittest.skipUnless(sys.platform == "linux", "controlled smoke is Linux-only")
class ControlledFirstPartySmokeTests(unittest.TestCase):
    def test_first_party_success_does_not_attest_five_resource_trial(self):
        r = run_first_party_smoke("success")
        self.assertEqual(r.exit_code, 0)
        self.assertFalse(r.timed_out)
        self.assertGreater(r.wall_seconds, 0)
        self.assertGreaterEqual(r.cpu_seconds, 0)
        self.assertFalse(r.network_isolation_enforced)
        self.assertFalse(r.filesystem_isolation_enforced)
        self.assertFalse(r.full_five_resource_trial_attested)
        self.assertFalse(r.tokens_metered)
        self.assertFalse(r.gpu_metered)

    def test_nonzero_exit_is_recorded(self):
        r = run_first_party_smoke("failure")
        self.assertEqual(r.exit_code, 7)
        self.assertFalse(r.timed_out)
        self.assertFalse(r.full_five_resource_trial_attested)

    def test_wall_timeout_kills_process_group(self):
        r = run_first_party_smoke("sleep", wall_limit_seconds=0.15)
        self.assertTrue(r.timed_out)
        self.assertNotEqual(r.exit_code, 0)
        self.assertLess(r.wall_seconds, 2)

    def test_no_user_supplied_shell_or_repository_commands(self):
        for invalid in ("__import__('os')", "python", "sh -c id", "../repo", "", 4):
            with self.subTest(invalid=invalid), self.assertRaises((ValueError, TypeError)):
                run_first_party_smoke(invalid)

    def test_reject_unsafe_or_unbounded_limits(self):
        with self.assertRaises(ValueError):
            run_first_party_smoke("success", wall_limit_seconds=float("inf"))
        with self.assertRaises(ValueError):
            run_first_party_smoke("success", cpu_hard_limit_seconds=1.2)


if __name__ == "__main__":
    unittest.main()
