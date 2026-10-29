# First executable first-party repair canary and next real-task gate

**29 October 2026 · U-CODE engineering milestone.**

This is an executed, deterministic **first-party Python microtask** with
seven *public* input/output fixtures, not an externally sourced repository
repair task, not an independent hidden oracle, not a trusted sandbox and
not treatment-versus-control AI-agent effectiveness evidence.

## What runs now in CI

`python -m scripts.smoke_first_party_executable_canary`

- The worker invokes the *currently installed Python interpreter* in a
  subprocess with `-I -S -c` and an immutable hardcoded first-party
  source string; no arbitrary code, no external checkout, no network
  API and no model inference.
- A tiny behavior contract is **stable ordered uniqueness** on integers.
  An intentionally faulty implementation uses sorted-set order. The
  fixed implementation preserves first occurrence order.
- Seven manually expected *public* fixtures live outside the worker's
  input. Their expected results are not sent to the child process.
- Intentionally faulty candidate: **4/7 public cases pass**;
  fixed first-party candidate: **7/7 public cases pass**.
- Both counts arise from actual deterministic Python execution, unlike
  hypothetical BES probability examples. They test evaluator plumbing,
  not a search algorithm. The worker source is SHA256-fingerprinted.
- Every receipt says external task admitted = false, independently
  sealed oracle = false, container isolation = false, authenticated
  five-resource meter = false, LLM inference = false, eligible for
  confirmatory evidence = false.
- These results must **NEVER** be inserted into Springer Results as
  real software repair evidence. A host Python process is **not a
  sandbox** for untrusted source code.

The tests inject malformed output, candidate substitutions, unexpected
stderr, wrong types, nonzero exits and simulated timeouts. The exposed
API takes **only one of two frozen first-party candidate IDs**.

## Optional, operator-controlled local rootless OCI preflight

The second-stage `scripts/probe_local_oci_first_party.py` **does not
run in CI and was not executed here** because a rootless local Docker
daemon, reviewed digest-pinned Python image and physical isolation
cannot be asserted by a GitHub-hosted chat environment. The
probe is not an external-task runner.

On a **dedicated, operator-approved host only**, after separately
reviewing local image provenance and the daemon:

```bash
# A real supply-chain-reviewed and locally cached immutable image digest
# must be supplied. This example variable is deliberately empty.
APPROVED_IMAGE=""

# With --image and no --execute: only validate/fingerprint the dry-run plan
python -m scripts.probe_local_oci_first_party --image "$APPROVED_IMAGE"

# Optional FIXED first-party print fixture, explicitly opt in:
python -m scripts.probe_local_oci_first_party --image "$APPROVED_IMAGE" --execute
```

`--execute` rejects explicit Docker remote host/context environment
variables, a non-local Unix socket context, a daemon that does not
**report** rootless mode, or a digest that is not in the locally
reported image cache. It then runs the previously reviewed
`docker run --pull=never --network=none --read-only --user=65534:65534`
contract with no host mount and a fixed Python print command, through
a timed Docker client invocation. These are **self-reported local
observations**: a mutable Docker CLI, daemon/socket, image, inspect
result or client can still be compromised. Client timeout does not
authenticate process-tree cleanup or a total CPU/GPU time bound.
A passing probe does **not** authorize external source execution.

## First real task: PHP #104 decision is still blocked

The strongest near-term repository task lead is
[mvdbos/php-spider PR #172](https://github.com/mvdbos/php-spider/pull/172),
candidate 104, pinned pre-fix base
`25e9b1cf855669c24ba1609c7d4cfcda17ac6217`.

Read-only current public issue checks reaffirmed:

| Artifact | Created (UTC) | Last updated (UTC) |
| --- | --- | --- |
| Parent issue #166 | 2026-10-22 22:52:00 | 2026-10-23 09:03:25 |
| Child issue #168 | 2026-10-22 22:53:10 | 2026-10-22 23:03:40 |
| PR #172 | 2026-10-22 22:55:42 | 2026-10-22 23:05:24 |

**These timestamps do not attest the actual issue-body text at
22:55:42 UTC.** GitHub's issue timeline lacks a trustworthy full
historical text snapshot; the issue body was subsequently updated.
Do not recover "original" requirements from the solution PR, cite
the PR's own tests as an independent oracle, or silently promote
PHP #104 to an admitted historical task.

The [source-era contract packet](PHP104_BASE_SOURCE_CONTRACT_REVIEW_2026-10-28.md)
and [oracle review blueprint](PHP104_INDEPENDENT_ORACLE_REVIEW_PLAN_2026-10-28.md)
remain metadata and prospectively proposed test families only.

Two distinct next routes:

**Path A — historical task.** Obtain independently verifiable
pre-PR issue text (e.g. authenticated contemporaneous archival
artifact), independent code-rights review, a separate hidden
full-task functional oracle, pinned PHP dependencies and an
observably isolated runner. A creation timestamp is not an archive.

**Path B — prospective task.** Obtain two independent reviewers'
signoff on a newly ratified behavior contract from the original base
code, record its own first-availability/creation date and file rights,
write independent evaluator-only cases, and classify the task as
**NEW PROSPECTIVE**, never as historical Copilot performance.
Keep the A/B denominators and cohorts separate in all tables.

In both routes, no GPU/API model inference or matched eight-policy
full-repository effectiveness claim is permitted until *all* independent
research and execution gates pass.

## Run verification

```bash
python -m unittest discover -s tests -v
python -m scripts.smoke_first_party_executable_canary
python -m scripts.check_local_readiness
python -m scripts.verify_php104_oracle_blueprint
```

The first-party microtask and the rootless OCI operator probe are
two separate stages: **working test plumbing** versus **unverified
runtime sandbox observations**. Neither is independent task
admission. No private oracle gold, source model weights or third-party
repository material is added to the public repository.
