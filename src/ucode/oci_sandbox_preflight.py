"""Dry-run, deny-by-default OCI container launch contract for U-CODE.

Only a fixed first-party Python smoke is permitted. No network, Docker,
subprocess or repository code is invoked by this module; constructed argv is
NOT permission to run external software. Actual container isolation must be
independently inspected and tested on an authorized dedicated host.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

_IMAGE = re.compile(
    r"^[a-z0-9][a-z0-9._/-]{1,180}@sha256:[0-9a-f]{64}$"
)
# The fixture is hardcoded. No shell, user code, command or volume input.
_FIXTURE = "print('U-CODE synthetic OCI preflight fixture')"
_CPU_SHARES = 1_000_000_000
_NOFILE = 64
_UID = 65534
_TMPFS = "/tmp:rw,nosuid,nodev,noexec,size=67108864,uid=65534,gid=65534"


@dataclass(frozen=True)
class DryRunLimits:
    memory_mib: int = 256
    max_pids: int = 32
    cpu_seconds_per_process: int = 2
    max_wall_seconds_for_future_supervisor: int = 5

    def __post_init__(self):
        if (type(self.memory_mib) is not int or
                not 128 <= self.memory_mib <= 4096):
            raise ValueError("memory MiB must be an integer in [128,4096]")
        if type(self.max_pids) is not int or not 1 <= self.max_pids <= 64:
            raise ValueError("pids limit must be an integer in [1,64]")
        if (type(self.cpu_seconds_per_process) is not int or
                not 1 <= self.cpu_seconds_per_process <= 10):
            raise ValueError("CPU ulimit must be an integer in [1,10]")
        if (type(self.max_wall_seconds_for_future_supervisor) is not int
                or not 1 <= self.max_wall_seconds_for_future_supervisor <= 20):
            raise ValueError("future wall-clock deadline must be in [1,20]")


@dataclass(frozen=True)
class DryRunSandboxPlan:
    """An inspectable proposal, never an approved real-task runner."""

    image_ref: str
    limits: DryRunLimits
    argv: tuple[str, ...]
    argv_sha256: str
    stage: str = "DRY_RUN_FIRST_PARTY_FIXED_FIXTURE_NOT_EXECUTED"
    executed: bool = False
    runtime_daemon_rootless_verified: bool = False
    network_denial_observed: bool = False
    filesystem_isolation_observed: bool = False
    runtime_seccomp_verified: bool = False
    independently_attested_five_resource_limits: bool = False
    permitted_to_execute_untrusted_repositories: bool = False


def _render(image_ref: str, limits: DryRunLimits) -> tuple[str, ...]:
    memory = limits.memory_mib * 1024 * 1024
    cpu = limits.cpu_seconds_per_process
    return (
        "docker", "run", "--rm", "--pull=never",
        # Docker's private PID and UTS namespaces are the safe defaults.
        # Docker HostConfig accepts an EMPTY mode for both, not "private".
        "--network=none", "--ipc=private", "--cgroupns=private",
        "--read-only", "--user=65534:65534",
        "--cap-drop=ALL", "--security-opt=no-new-privileges",
        "--pids-limit=" + str(limits.max_pids),
        "--memory=" + str(memory),
        "--memory-swap=" + str(memory),
        "--cpus=1",
        "--ulimit=cpu=" + str(cpu) + ":" + str(cpu),
        "--ulimit=nofile=64:64",
        "--tmpfs=" + _TMPFS,
        "--workdir=/tmp",
        "--entrypoint=/usr/local/bin/python3",
        image_ref, "-I", "-S", "-c", _FIXTURE,
    )


def _digest(argv: tuple[str, ...]) -> str:
    return sha256(json.dumps(
        argv, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")).hexdigest()


def propose_first_party_container(
    image_ref: str, limits: DryRunLimits = DryRunLimits(),
) -> DryRunSandboxPlan:
    """Create strict command tokens WITHOUT executing or resolving an image.

    A pinned-looking sha256 is a syntactic image selector, NOT proof that
    the blob exists, the registry is trustworthy or the daemon is rootless.
    No default image is provided: a real operator must obtain the exact
    digest through a separate approved supply-chain process.
    """
    if not isinstance(image_ref, str) or not _IMAGE.fullmatch(image_ref):
        raise ValueError("OCI image requires exact normalized digest ref")
    if not isinstance(limits, DryRunLimits):
        raise TypeError("typed first-party dry-run limits required")
    if image_ref.startswith(("/", "-", ".")) or ".." in image_ref:
        raise ValueError("invalid image path")
    argv = _render(image_ref, limits)
    return DryRunSandboxPlan(image_ref, limits, argv, _digest(argv))


def validate_dry_run_plan(plan: DryRunSandboxPlan) -> str:
    """Fail if a command, fixture, quota or approval status was modified.

    This is *structural* integrity, not a signature or observed isolation.
    """
    if not isinstance(plan, DryRunSandboxPlan):
        raise TypeError("typed dry-run plan required")
    rebuilt = propose_first_party_container(plan.image_ref, plan.limits)
    if (plan != rebuilt or type(plan.argv) is not tuple
            or any(type(s) is not str for s in plan.argv)):
        raise ValueError("plan altered, or falsely promoted to executed/approved")
    return "STRUCTURAL_DRY_RUN_ONLY_NOT_HARDENED_CONTAINER"


@dataclass(frozen=True)
class InspectShapeAudit:
    """Untrusted JSON shape from docker inspect; no authenticated observation."""

    declared_profile_matches: bool
    command_sha256: str
    externally_authenticated: bool = False
    measured_network_isolation: bool = False
    host_daemon_rootless_proven: bool = False
    independent_seccomp_proven: bool = False
    filesystem_containment_proven: bool = False
    approved_external_task_runner: bool = False


def check_untrusted_inspect_shape(
    plan: DryRunSandboxPlan, inspect: dict,
) -> InspectShapeAudit:
    """Verify a supplied Docker-inspect-like object describes strict defaults.

    Arbitrary callers can forge this dict, so success NEVER grants execution
    permission or claims actual network/seccomp/mount isolation.
    """
    validate_dry_run_plan(plan)
    if not isinstance(inspect, dict):
        raise TypeError("typed inspection object required")
    cfg=inspect.get("Config")
    host=inspect.get("HostConfig")
    if not isinstance(cfg, dict) or not isinstance(host, dict):
        raise ValueError("Config and HostConfig required")
    expected={
        "NetworkMode": "none", "PidMode": "",
        "IpcMode": "private", "UTSMode": "",
        "CgroupnsMode": "private", "ReadonlyRootfs": True,
        "Privileged": False, "CapAdd": [],
        "CapDrop": ["ALL"], "SecurityOpt": ["no-new-privileges"],
        "Binds": [], "Mounts": [], "Devices": [], "DeviceRequests": [],
        "PidsLimit": plan.limits.max_pids,
        "Memory": plan.limits.memory_mib * 1024 * 1024,
        "MemorySwap": plan.limits.memory_mib * 1024 * 1024,
        "NanoCpus": _CPU_SHARES,
        "Tmpfs": {"/tmp":"rw,nosuid,nodev,noexec,size=67108864,uid=65534,gid=65534"},
    }
    for key,value in expected.items():
        if key not in host or type(host[key]) is not type(value) or host[key]!=value:
            raise ValueError("inspection mismatch/unsupported host control: "+key)
    if (cfg.get("Image") != plan.image_ref
            or cfg.get("User") != "65534:65534"
            or cfg.get("WorkingDir") != "/tmp"
            or cfg.get("Entrypoint") != ["/usr/local/bin/python3"]
            or cfg.get("Cmd") != ["-I","-S","-c",_FIXTURE]):
        raise ValueError("inspection image, identity or fixed command mismatch")
    ulimits=host.get("Ulimits")
    expected_ulimits=[
        {"Name":"cpu","Soft":plan.limits.cpu_seconds_per_process,
         "Hard":plan.limits.cpu_seconds_per_process},
        {"Name":"nofile","Soft":_NOFILE,"Hard":_NOFILE},
    ]
    if (type(ulimits) is not list
            or sorted(ulimits,key=lambda x: x.get("Name","")) != expected_ulimits):
        raise ValueError("inspection ulimits mismatch")
    if inspect.get("Mounts") != []:
        raise ValueError("host mounts in inspection are forbidden")
    network=inspect.get("NetworkSettings")
    if not isinstance(network,dict) or network.get("Networks") != {"none": {}}:
        raise ValueError("unexpected Docker network attachment")
    return InspectShapeAudit(True,plan.argv_sha256)
