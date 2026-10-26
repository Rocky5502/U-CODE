"""Policy-neutral five-resource metering evidence and first-party smoke harness.

STRUCTURAL validation only: source names, receipt hashes and enforcement flags
are declarative, not independently signed or verified. This is NOT a trusted
runner, physical network isolation, a model inference meter or task admission.

No third-party repository code, arbitrary command, shell or user script can be
passed to the subprocess helper. It executes only hardcoded first-party fixtures.
"""

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from numbers import Real
import os
import re
import signal
import subprocess
import sys
import time

RESOURCE_FIELDS = ("tokens", "test_calls", "gpu_seconds", "cpu_seconds", "wall_seconds")
INTEGER_FIELDS = frozenset(("tokens", "test_calls"))
SOURCE_BY_RESOURCE = {
    "tokens": "trusted_engine_accounting",
    "test_calls": "runner_test_dispatch_log",
    "gpu_seconds": "gpu_driver_accounting",
    "cpu_seconds": "os_child_rusage",
    "wall_seconds": "os_monotonic_clock",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class MeteringAttestationError(ValueError):
    """Fail-closed missing, conflicting or unauditable meter evidence."""


def _valid_quantity(field: str, amount: object) -> bool:
    if field in INTEGER_FIELDS:
        return type(amount) is int and amount >= 0
    return (isinstance(amount, Real) and not isinstance(amount, bool)
            and isfinite(amount) and amount >= 0)


@dataclass(frozen=True)
class MeterReading:
    """A claimed meter reading, not proof that the claimed source is genuine."""

    amount: float | int
    source: str
    receipt_sha256: str
    independent_of_policy: bool
    cap_enforced: bool


@dataclass(frozen=True)
class StructuralMeteringAudit:
    """Consistent evidence SHAPE; never an authorized real-trial certificate."""

    run_id: str
    consumed: tuple[tuple[str, float | int], ...]
    source_fingerprints: tuple[tuple[str, str], ...]
    structural_checks_passed: bool = True
    externally_verified: bool = False
    real_trial_approved: bool = False


def check_five_resource_evidence(
    run_id: str,
    caps: dict[str, float | int],
    readings: dict[str, MeterReading],
) -> StructuralMeteringAudit:
    """Require independently observed AND separately enforced nominal caps.

    Caller-provided claimed source, receipt digest and booleans are checked for
    structural soundness, not authenticated. Independent verifier signoff,
    meter integration, and physical limits are mandatory before any real trial.
    Missing/unenforced tokens, tests or GPU dimensions fail even if reported 0.
    """
    if not isinstance(run_id, str) or not run_id.strip() or len(run_id) > 128:
        raise MeteringAttestationError("nonempty bounded run identifier required")
    if not isinstance(caps, dict) or set(caps) != set(RESOURCE_FIELDS):
        raise MeteringAttestationError("exact five-component cap required")
    if not isinstance(readings, dict) or set(readings) != set(RESOURCE_FIELDS):
        raise MeteringAttestationError("all five separately metered components required")
    measured = []
    proofs = []
    for field in RESOURCE_FIELDS:
        cap = caps[field]
        reading = readings[field]
        if not _valid_quantity(field, cap):
            raise MeteringAttestationError("invalid resource cap: " + field)
        if not isinstance(reading, MeterReading):
            raise MeteringAttestationError("typed reading missing: " + field)
        if not _valid_quantity(field, reading.amount):
            raise MeteringAttestationError("invalid reading: " + field)
        if reading.amount > cap:
            raise MeteringAttestationError("resource exceeds enforced cap: " + field)
        if reading.source != SOURCE_BY_RESOURCE[field]:
            raise MeteringAttestationError("wrong or model-self-reported source: " + field)
        if (reading.independent_of_policy is not True
                or reading.cap_enforced is not True):
            raise MeteringAttestationError("not independently metered AND enforced: " + field)
        if (not isinstance(reading.receipt_sha256, str)
                or not HEX64.fullmatch(reading.receipt_sha256)):
            raise MeteringAttestationError("immutable source receipt SHA256 required: " + field)
        measured.append((field, reading.amount))
        proofs.append((field, reading.receipt_sha256))
    return StructuralMeteringAudit(run_id, tuple(measured), tuple(proofs))


# First-party fixtures are constants: no arbitrary subprocess source, user argv,
# shell interpolation, file checkout, model, token or test-runner integration.
_FIRST_PARTY_FIXTURES = {
    "success": "print('U-CODE isolated-python smoke fixture')",
    "failure": "raise SystemExit(7)",
    "sleep": "import time; time.sleep(4)",
}


@dataclass(frozen=True)
class FirstPartySmokeResult:
    fixture: str
    exit_code: int | None
    timed_out: bool
    wall_seconds: float
    cpu_seconds: float
    wall_limit_seconds: float
    cpu_hard_limit_seconds: int
    output_sha256: str
    cpu_meter: str = "aggregate_os_child_rusage_delta_not_per_process"
    wall_meter: str = "independent_os_monotonic_clock"
    wall_kill_implemented: bool = True
    cpu_rlimit_implemented: bool = True
    network_isolation_enforced: bool = False
    filesystem_isolation_enforced: bool = False
    tokens_metered: bool = False
    tests_metered: bool = False
    gpu_metered: bool = False
    full_five_resource_trial_attested: bool = False


def run_first_party_smoke(
    fixture: str,
    *,
    wall_limit_seconds: float = 2.0,
    cpu_hard_limit_seconds: int = 2,
) -> FirstPartySmokeResult:
    """Controlled POSIX subprocess smoke, intentionally NOT a secure sandbox.

    CPU is measured via process-global RUSAGE_CHILDREN delta: contamination is
    possible if OTHER subprocesses finish concurrently. This conservative
    contract never promotes such a reading to an approved production meter.
    RLIMIT_CPU has integer-second granularity; wall timeout uses process-group
    kill. Network namespace, containers and model/test/GPU meters are absent.
    """
    if fixture not in _FIRST_PARTY_FIXTURES:
        raise ValueError("only predefined first-party fixtures are executable")
    if sys.platform != "linux":
        raise RuntimeError("first-party metering smoke currently Linux-only")
    if (not isinstance(wall_limit_seconds, Real) or isinstance(wall_limit_seconds, bool)
            or not isfinite(wall_limit_seconds) or not 0 < wall_limit_seconds <= 10):
        raise ValueError("finite positive wall limit at most ten seconds required")
    if type(cpu_hard_limit_seconds) is not int or not (1 <= cpu_hard_limit_seconds <= 10):
        raise ValueError("integer CPU rlimit between one and ten seconds required")
    import resource  # unavailable on Windows; Linux-only check above
    import tempfile

    def limit_cpu():
        resource.setrlimit(resource.RLIMIT_CPU,
                           (cpu_hard_limit_seconds, cpu_hard_limit_seconds))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    # Do not claim to isolate filesystem, network or resource accounting.
    with tempfile.TemporaryDirectory(prefix="ucode-firstparty-meter-") as directory:
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        started = time.monotonic()
        proc = subprocess.Popen(
            [sys.executable, "-I", "-S", "-c", _FIRST_PARTY_FIXTURES[fixture]],
            cwd=directory, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env={"PATH": "/usr/bin:/bin"},
            start_new_session=True, preexec_fn=limit_cpu,
        )
        timed_out = False
        try:
            stdout, stderr = proc.communicate(timeout=wall_limit_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
        duration = time.monotonic() - started
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = ((after.ru_utime + after.ru_stime)
               - (before.ru_utime + before.ru_stime))
        return FirstPartySmokeResult(
            fixture, proc.returncode, timed_out, max(0.0, duration),
            max(0.0, cpu), float(wall_limit_seconds), cpu_hard_limit_seconds,
            sha256(stdout + b"\0" + stderr).hexdigest(),
        )
