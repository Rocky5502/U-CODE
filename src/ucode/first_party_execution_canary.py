"""Trusted-source, executable repair canary for U-CODE evaluation plumbing.

Unlike forecast-only unit tests, this runs TWO fixed first-party functions
inside a short-lived Python subprocess and evaluates independent *public*
input/output cases. It deliberately never executes downloaded repository
code, LLM output, user-provided Python, Docker commands or evaluator gold.

This is NOT a qualified SWE-bench task, sealed evaluator, sandbox, physical
resource meter, model comparison, or empirical research outcome.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

_BAD = "sorts_unique_instead_of_preserving_order"
_FIXED = "stable_unique_repair"
ALLOWED_FIRST_PARTY_CANDIDATES = (_BAD, _FIXED)
STAGE = "EXECUTED_PUBLIC_FIRST_PARTY_CANARY_NOT_RESEARCH_BENCHMARK"
# Public, manually specified expected behavior. The worker receives the
# INPUTS only; it never sees expected outputs or a hidden oracle credential.
_CASES: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...] = (
    ((), ()),
    ((2,), (2,)),
    ((2, 1, 2), (2, 1)),
    ((0, 3, 0, 2), (0, 3, 2)),
    ((4, 4, 4), (4,)),
    ((9, 1, 9, 5, 1), (9, 1, 5)),
    ((1, 2, 3), (1, 2, 3)),
)
# Source is entirely FIRST PARTY and hardcoded. Never interpolate input,
# accept a source path, import repository packages, or run a shell.
_WORKER = """import json
import sys

request = json.load(sys.stdin)
choice = request["candidate"]
cases = request["cases"]
if choice not in ("sorts_unique_instead_of_preserving_order", "stable_unique_repair"):
    raise ValueError("unrecognized first-party canary candidate")
output = []
for seq in cases:
    if choice == "sorts_unique_instead_of_preserving_order":
        answer = sorted(set(seq))  # intentional tiny repair regression
    else:
        answer = []
        seen = set()
        for number in seq:
            if number not in seen:
                seen.add(number)
                answer.append(number)
    output.append(answer)
json.dump({"candidate": choice, "outputs": output}, sys.stdout)
"""
_WORKER_SHA256 = sha256(_WORKER.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FirstPartyExecutionReceipt:
    """Literal executed fixture, with no real-task approval privilege."""
    stage: str
    candidate: str
    worker_source_sha256: str
    attempted_public_cases: int
    passed_public_cases: int
    failed_public_cases: int
    output_sha256: str
    fixed_first_party_source_executed: bool = True
    user_supplied_code_executed: bool = False
    third_party_source_executed: bool = False
    genuine_repository_task_admitted: bool = False
    held_out_independent_oracle_verified: bool = False
    sandbox_isolation_verified: bool = False
    five_resource_physical_meter_authenticated: bool = False
    llm_inference_executed: bool = False
    eligible_as_confirmatory_evidence: bool = False


def run_first_party_execution_canary(candidate: str) -> FirstPartyExecutionReceipt:
    """Execute only one of two frozen first-party functions; return public scores.

    The subprocess is deliberately NOT an isolation boundary: it runs under
    the caller's user identity. Do not reuse this function for third-party
    patches even if the invocation succeeds on CI.
    """
    if type(candidate) is not str or candidate not in ALLOWED_FIRST_PARTY_CANDIDATES:
        raise ValueError("only two frozen first-party canary candidates permitted")
    req = {"candidate": candidate, "cases": [list(x) for x, _ in _CASES]}
    with TemporaryDirectory(prefix="ucode-first-party-canary-") as temp:
        try:
            process = subprocess.run(
                [sys.executable, "-I", "-S", "-c", _WORKER],
                input=json.dumps(req, separators=(",", ":")),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8",
                cwd=Path(temp), timeout=3, check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            raise RuntimeError("first-party canary execution failed or timed out") from exc
    if process.returncode != 0:
        raise RuntimeError("first-party canary worker exited nonzero")
    if len(process.stdout) > 65536 or process.stderr:
        raise ValueError("unexpected first-party worker output")
    try:
        result = json.loads(process.stdout)
    except (TypeError, ValueError) as exc:
        raise ValueError("worker emitted invalid JSON") from exc
    if (type(result) is not dict or set(result) != {"candidate", "outputs"}
            or result["candidate"] != candidate
            or type(result["outputs"]) is not list
            or len(result["outputs"]) != len(_CASES)):
        raise ValueError("worker result schema or candidate identity mismatch")
    for output in result["outputs"]:
        if type(output) is not list or any(type(x) is not int for x in output):
            raise ValueError("worker output must be lists of integers")
    passed = sum(output == list(expected)
                 for output, (_, expected) in zip(result["outputs"], _CASES))
    return FirstPartyExecutionReceipt(
        stage=STAGE, candidate=candidate, worker_source_sha256=_WORKER_SHA256,
        attempted_public_cases=len(_CASES), passed_public_cases=passed,
        failed_public_cases=len(_CASES)-passed,
        output_sha256=sha256(process.stdout.encode("utf-8")).hexdigest(),
    )


def check_first_party_repair_canary() -> dict:
    """Smoke-test both executable fixed implementations, never imply efficacy."""
    bad = run_first_party_execution_canary(_BAD)
    good = run_first_party_execution_canary(_FIXED)
    if (bad.attempted_public_cases != 7 or good.attempted_public_cases != 7
            or bad.passed_public_cases != 4 or good.passed_public_cases != 7
            or bad.worker_source_sha256 != good.worker_source_sha256):
        raise AssertionError("trusted first-party repair canary outcome drift")
    return {
        "status": STAGE,
        "worker_sha256": _WORKER_SHA256,
        "candidate_receipts": [bad.__dict__, good.__dict__],
        "distinct_frozen_first_party_candidate_implementations": 2,
        "public_fixture_cases_per_implementation": len(_CASES),
        "untrusted_source_executed": False,
        "real_repository_tasks_admitted": 0,
        "authenticated_hidden_oracles": 0,
        "real_policy_comparison_results": 0,
        "qualified_experimental_effect": None,
    }
