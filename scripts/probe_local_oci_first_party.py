"""Opt-in LOCAL Docker verification probe for a fixed first-party fixture.

NO third-party task execution; no arbitrary image downloads, commands,
mounts, source code, network, model or gold. A compliant Docker inspect/
rootless report is only SELF-REPORTED LOCAL EVIDENCE, not independent
certification of daemon provenance, network denial, security or five
resource meters. Never auto-promote real-run approval from this probe.

Usage (only after independent image/supply-chain approval):
python -m scripts.probe_local_oci_first_party --image \
    docker.io/library/python@sha256:<REAL_PINNED_LOCAL_IMAGE_DIGEST> --execute

No --execute => no Docker subprocess.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
import subprocess
from typing import Sequence

from ucode.oci_sandbox_preflight import (
    DryRunLimits, propose_first_party_container, validate_dry_run_plan,
)

_EXPECTED = "U-CODE synthetic OCI preflight fixture"


def _local_docker_command(tokens: Sequence[str], timeout: int = 5) -> str:
    """No shell, fixed trusted command tokens; reject nonzero/error output."""
    try:
        proc = subprocess.run(
            list(tokens), text=True, encoding="utf-8",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("local Docker command unavailable or timed out") from exc
    if proc.returncode != 0 or len(proc.stdout) > 65536:
        raise RuntimeError("local Docker command exited nonzero or emitted oversized output")
    return proc.stdout.strip()


def _read_json(command: tuple[str, ...]) -> object:
    raw = _local_docker_command(command)
    try:
        return json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("local Docker command produced invalid JSON") from exc


def probe_local_first_party_oci(
    image_ref: str, *, execute: bool = False,
    limits: DryRunLimits = DryRunLimits(),
) -> dict:
    """Validate/fingerprint a plan; execute only after deliberate opt-in.

    Reports Docker daemon/source attestations as untrusted observations.
    Command composition never accepts user-controlled code, flags, mounts,
    containers, image pull or network access from callers.
    """
    plan = propose_first_party_container(image_ref, limits)
    validate_dry_run_plan(plan)
    base = {
        "stage": "OCI_LOCAL_FIRST_PARTY_PREFLIGHT_ONLY",
        "image_ref": plan.image_ref,
        "argv_sha256": plan.argv_sha256,
        "docker_probed": False,
        "fixed_fixture_executed": False,
        "docker_reported_rootless": False,
        "local_unix_context_reported": False,
        "local_pinned_image_reported": False,
        "fixture_stdout_exact": False,
        "independently_authenticated_isolation": False,
        "independently_verified_no_network": False,
        "five_resource_meter_authenticated": False,
        "independently_admitted_real_repository_tasks": 0,
        "permitted_to_execute_third_party_code": False,
        "real_trial_approved": False,
    }
    if type(execute) is not bool:
        raise TypeError("execution opt-in must be explicit boolean")
    if not execute:
        return base
    if os.environ.get("DOCKER_HOST") or os.environ.get("DOCKER_CONTEXT"):
        raise ValueError("environment-selected Docker daemon/context is prohibited")
    context = _read_json((
        "docker", "context", "inspect", "--format",
        "{{json .Endpoints.docker.Host}}",
    ))
    if (type(context) is not str or not context.startswith("unix:///")
            or not context[8:] or ".." in context[8:]):
        raise ValueError("Docker context must report a local Unix socket")
    security = _read_json((
        "docker", "info", "--format", "{{json .SecurityOptions}}",
    ))
    if (type(security) is not list or any(type(x) is not str for x in security)
            or not any(x in ("name=rootless", "rootless") for x in security)):
        raise ValueError("Docker daemon does not report rootless security mode")
    digests = _read_json((
        "docker", "image", "inspect", "--format", "{{json .RepoDigests}}",
        plan.image_ref,
    ))
    if type(digests) is not list or plan.image_ref not in digests:
        raise ValueError("requested pinned image not reported in local cache")
    # Docker client timeout is NOT guaranteed to kill detached daemon children.
    # This fixed print fixture terminates immediately; never reuse for
    # arbitrary external code or a supposedly hardened container runner.
    stdout = _local_docker_command(
        plan.argv, timeout=limits.max_wall_seconds_for_future_supervisor,
    )
    if stdout != _EXPECTED:
        raise ValueError("unexpected first-party container fixture result")
    return {
        **base,
        "docker_probed": True,
        "fixed_fixture_executed": True,
        "docker_reported_rootless": True,
        "local_unix_context_reported": True,
        "local_pinned_image_reported": True,
        "fixture_stdout_exact": True,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image", required=True,
                   help="Approved locally cached OCI image digest only; never a tag")
    p.add_argument("--execute", action="store_true",
                   help="Explicitly permit only a fixed first-party print fixture")
    args = p.parse_args()
    print(json.dumps(
        probe_local_first_party_oci(args.image, execute=args.execute),
        indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
