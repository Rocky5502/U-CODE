# Security policy and threat model

## Supported scope

U-CODE is a research prototype; **its current repository does not contain a security-attested sandbox for arbitrary third-party code**. Its OCI preflight constructs a proposed launch shape only. Passing unit tests or GitHub Actions is **not** a certification of isolation, safe shell execution, hidden-oracle integrity, or accurate GPU/CPU metering.

### Reporting vulnerabilities

Do **not** publish an exploit, token, hidden test or credential in a public issue.
Use GitHub's **Report a vulnerability** / private vulnerability reporting feature
on the repository's Security tab **if available**. If unavailable, contact
the maintainers privately through a channel listed on their official GitHub
profile; do not disclose secret material in public GitHub discussions.
Never assume this repository has a staffed security-response SLA.

## Before running anything

1. **First-party default:** `python -m pip install -r requirements.txt`,
   offline tests, metadata validation, model protocol planning, and
   source-only manuscript checking are allowed without importing or executing
   unknown PRs. Review any newly introduced dependency before installation.
2. **Third-party repositories:** do not run builds/tests on the host,
   notebook, GitHub Actions, privileged Docker daemon, or a container with
   host SSH/GitHub credentials. Require manually reviewed source-use rights
   and independent task admission.
3. **Containment (not yet implemented/attested):** disposable nonroot/rootless
   runner; no network; readonly or overlay pre-fix source; explicit writable
   temporary workspace; all mounts scoped; no Docker socket, host devices,
   SSH agent, home directory, tokens or cloud metadata access.
4. **Enforcement:** cgroups/pids/memory/CPU limits, wall timeout, immutable
   container image digest, checked language toolchains, process tree cleanup,
   file/path traversal and symlink defenses, disk quota, and independent
   token/test/GPU/CPU/wall accounting. The current preflight is **not this**.
5. **Model adapters:** never use unreviewed `trust_remote_code` or
   implicitly download unpinned checkpoints. Prefer loopback-only local
   model endpoints. Model output is untrusted data, **never a shell command
   to execute directly**.
6. **Evaluation firewall:** gold patches, oracle logic, hidden tests,
   full post-fix PR descriptions, unrestricted issue histories, evaluator
   credentials and final correctness labels are **never policy-visible**.
   Store any future sealed evaluator outside the repository's public tree.
7. **Secrets:** use local environment variables/separate secure credential
   storage; never commit `.env`, API tokens, passwords, private keys,
   research participant data, gated model weights or raw third-party datasets.
   Rotate and revoke immediately if accidentally exposed.
8. **Licenses:** the project's MIT license covers its original source only.
   Dataset and model terms are separately reviewed per artifact. No
   automatic rights approval based on a root SPDX string.

## CI permissions and trust boundaries

The default CI uses `permissions: contents: read`, Python 3.10/3.12 and
first-party offline scripts. It **must not** add raw external source checkouts,
untrusted PR shell scripts, self-hosted privileged runners, credentials,
unvetted actions, hidden oracle files or live model calls. New external
dependencies require review and version pinning; source archives, datasets,
weights and execution traces stay out of default CI.

## Known research blockers

- **0** independent admitted executable tasks and **0** sealed evaluators.
- Rootless isolation/network-disable and five-vector meters are not attested.
- All six model licenses/checkpoint/runtime compatibility gates remain pending.
- Synthetic algorithm and tamper-resistance tests establish structural
  properties, **not a production safety guarantee**.

See [local experiment protocol](docs/LOCAL_EXPERIMENTS.md),
[admission gates](src/ucode/task_admission.py), [OCI dry-run](docs/OCI_SANDBOX_LAUNCH_PREFLIGHT_2026-10-29.md),
[data governance](docs/DATA_GOVERNANCE.md).
