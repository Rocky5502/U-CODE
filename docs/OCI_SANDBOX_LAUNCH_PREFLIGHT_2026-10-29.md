# U-CODE — deny-by-default OCI launch preflight (29 October 2026)

**Status: STRICT NON-EXECUTING, FIRST-PARTY DOCKER-COMMAND CONTRACT.**
Not a hardened sandbox, runtime/daemon attestation, model run,
external task admission, oracle isolation, or complete five-resource quota.

## Why this is the next P0-2 step

The existing `metering_attestation.py` has a real Linux first-party
subprocess smoke with CPU RLIMIT and an outer wall timeout, and
`task_gate.py` checks declarations. Neither constructs a concrete,
reviewable no-network container command for later untrusted source code.
The new `src/ucode/oci_sandbox_preflight.py` fills that **planning**
gap. It returns a canonical tuple of Docker tokens, its SHA256 and
flags which remain *permanently false* for executed/approved/isolated.
No Docker/subprocess call exists in the new module.

The prospective launch contract is intentionally restricted to:
- A required syntactically digest-pinned, lowercased OCI image reference
  (`...@sha256:<64 lowercase hex>`) with `--pull=never`.
  A valid-looking digest is **not** a fetched or authenticated image.
- A hardcoded first-party Python print fixture, `python3 -I -S -c`;
  **no arbitrary command, third-party repository source or patch**.
- `--network=none`, `--read-only`, numeric non-root user `65534:65534`,
  `--cap-drop=ALL`, `--security-opt=no-new-privileges`,
  no host `--mount`/`-v`, an exact `/tmp` tmpfs with `noexec,nosuid,nodev`.
- Memory and memory-swap restrictions, a limited process count,
  a one-CPU *rate* quota, `RLIMIT_CPU` *per process*, and a file-descriptor
  limit. These **do not** independently enforce total CPU-seconds,
  total GPU-seconds, tokens, test calls or wall seconds.
- An explicit `max_wall_seconds_for_future_supervisor` value that
  **is not currently enforced**, since this script does not launch a
  subprocess. The future external supervisor must enforce a real
  process-tree kill and record independent consumption.

`check_untrusted_inspect_shape` additionally rejects a *caller-supplied*
Docker-inspect-shaped record that reports extra capabilities, privileged
mode, host network, writable root, mounts/devices, wrong task identity,
unexpected image/entrypoint, weaker memory/PID/CPU controls, or a
different network attachment. Passing that check **does not authenticate
the dict** or prove a particular daemon/namespace actually implemented
the controls. Rootless *daemon*, enforced seccomp, cgroup boundaries,
network-denial probes, side channels, OOM behavior and measured total
resource limits need separate observed evidence and review.

## Exact offline commands (safe to run in standard CI)

```bash
python -m scripts.smoke_oci_sandbox_preflight
python -m unittest discover -s tests -v
```

The smoke prints a digest of the canonical argument tuple and an image
reference with `sha256:aaaa...`, explicitly labeled **fake syntax fixture**.
**Do not run or pull that image.** CI never invokes Docker for this
preflight and never executes user-supplied source.

## Adversarial test matrix

The new tests corrupt network mode, mount lists, device requests,
privilege flags, UID, image reference, entrypoint, command, ulimits,
memory-swap, CPU quota, PID limit, or attempt to self-promote success;
every mutation must fail closed. Even a perfectly shaped `docker
inspect` dictionary yields `approved_external_task_runner=False`.

## Evidence needed before any third-party repository may execute

1. Source-level permission review and a verifiably immutable pre-fix
   task+repository snapshot, performed by independent reviewers.
2. A real, privilege-reviewed, rootless daemon on a dedicated machine;
   pinned, offline-available image layers, approved SBOM and supply chain.
3. Runtime inspection **plus observed negative tests** for network,
   filesystem read/write, privilege escalation, dangerous devices,
   retained children, escaped processes and evaluator/test-secret access.
4. Independent process/container metering for all **five** dimensions
   (tokens, test calls, GPU, CPU, wall) with hard limit enforcement;
   the Docker arguments here do **not** provide all five.
5. A trusted host-side wall-clock supervisor and robust process-tree
   shutdown, verified under crash and timeout conditions.
6. Full prompt/test/oracle separation and strictly evaluator-only
   post-termination functional correctness results.
7. A reviewer-approved real task and a frozen study receipt linking the
   exact approved image, task, tool set, model revision, seed, policy,
   action archive and budget for both primary comparator arms.

**No P0-2, P0-1 or P0-3 real study gate has been passed.** Do not
submit synthetic outcomes as Springer RQ3 measurements.
