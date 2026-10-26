# U-CODE — Policy-Neutral Metering Attestation Gate (2026-10-27)

**Research status:** structural, first-party, offline code only. **Not** a trusted physical metering certificate, hardened sandbox, or completed real-task evaluation.

## Purpose

The U-CODE versus optimized uncertainty-free control requires equal, separately enforced caps on tokens, test calls, GPU seconds, CPU seconds and wall seconds. A planning budget, a language model's reported cost or an ordinary policy receipt boolean is not proof of an actual independently metered run. Both treatment and control must share trustworthy measurement and enforcement.

The new Python module src/ucode/metering_attestation.py implements a fail-closed **evidence-shape** gate and a Linux-only, fixed first-party subprocess smoke harness. tests/test_metering_attestation.py adds 14 adversarial cases and timeout/exit checks. Both components are original first-party code; no GitHub candidate repository code is executed.

## Structural contract

Every one of the five dimensions must be present as a typed reading with a nonnegative finite amount, a dimension-specific counter source, an immutable receipt SHA256, independent-of-policy evidence indicator, and a separately enforced cap indicator. Tokens and test calls must be integral. Quantities above cap, omitted fields (including zero-usage claims), model self-report, wrong source, NaN/inf, negative values, false enforcement indicators or invalid receipt hashes are rejected.

| Dimension | Required claimed source | Real enforcement and verification needed |
|---|---|---|
| Tokens | trusted_engine_accounting | independent engine callback and hard run-level token allowance |
| Test calls | runner_test_dispatch_log | trusted dispatcher counter and quota |
| GPU seconds | gpu_driver_accounting | attributed driver/scheduler telemetry and job quota |
| CPU seconds | os_child_rusage | attributed per-process/cgroup accounting and actual CPU cap |
| Wall seconds | os_monotonic_clock | independent monotonic deadline with full process-tree shutdown |

**A named source or SHA256 is not an authenticated receipt.** Caller-provided source labels and booleans could be forged. Accordingly StructuralMeteringAudit.externally_verified and StructuralMeteringAudit.real_trial_approved are ALWAYS false. Integration with a genuinely independent attestor remains a future task.

## Bounded first-party smoke

The only available workloads are fixed internal Python snippets: success, failure, and sleep. The API does not accept an arbitrary command, shell script, third-party repository path, user-supplied program, checkpoint or model code. The Linux subprocess uses isolated Python flags, a private temporary working directory, integer CPU RLIMIT, a wall timeout and process-group kill. It measures monotonic elapsed seconds and the before/after process-global RUSAGE_CHILDREN CPU delta.

Important limitations: RUSAGE_CHILDREN can be contaminated by concurrent child exits and is **not attributed to an individual process**; RLIMIT_CPU has integer-second resolution. There is NO separately enforced network namespace, rootless container, read-only filesystem, cgroups, independent per-process CPU meter, GPU accounting, model-token hook, trusted test dispatcher, physically isolated oracle or independent external approval. The smoke result explicitly says full_five_resource_trial_attested=False, network_isolation_enforced=False and filesystem_isolation_enforced=False. No real experiment may claim to have passed these gates based on this fixture.

## Action-receipt reconciliation and controlled CI smoke

The second [policy-neutral reconciliation module](../src/ucode/metering_reconciliation.py)
compares a five-resource `StructuralMeteringAudit` to **exactly one**
new immutable `SharedSession` receipt. It verifies unchanged
initial-budget and archive contracts; one appended action and trace;
canonical token/test/GPU/CPU/wall row ordering; exact five-component
agreement between structural meter readings and recorded consumption;
and the budget delta of each dimension. The binding returns the
before/after public trace SHA256 values and source-claim fingerprints,
with `independently_authenticated=False`,
`physical_caps_verified=False` and `approved_real_trial=False`
**unconditionally**. No policy receives an evaluator label.

A passing reconciliation is not proof that someone did not fabricate
`MeterReading.source`, hash strings or cap-enforcement booleans;
[the tests](../tests/test_metering_reconciliation.py) deliberately
demonstrate that a forged digest-shaped string cannot be authenticated
by a purely local data schema. In particular, an action whose reported
token use is two cannot be reconciled with a purported external reading
of one. Yet agreeing values alone are not evidence of physical truth.

GitHub Actions now also runs the fixed first-party
[`examples.metering_contract_smoke`](../examples/metering_contract_smoke.py)
in **both** Python-version jobs. It constructs a synthetic patch
and five-dimensional reading set, binds these to the public ledger,
and runs one hardcoded first-party subprocess success fixture. The
output explicitly reports `approved_real_trial=False`. There is no
arbitrary user or third-party code, model inference, network namespace,
sequestered evaluator or trusted GPU counter in this smoke.

**Verified offline checkpoint:** [CI run 40380919939](https://github.com/Rocky5502/U-CODE/actions/runs/40380919939)
passed **619 tests on Python 3.10** and **619 tests on Python 3.12**
and completed the additional first-party smoke on each interpreter.
The source-only [Overleaf artifact](https://github.com/Rocky5502/U-CODE/actions/runs/40380919939/artifacts/12678072294)
is packaged by GitHub, not synced to the authenticated live Overleaf
website. The checkpoint is about code checks, not measured effectiveness.

## Reproduction

Use a fresh checkout on Linux with the supported Python version, then run:

    python -m pip install -e .
    python -m unittest discover -s tests -v

GitHub Actions runs the above offline unit suite on Python 3.10 and 3.12. These synthetic/first-party tests check structural invariants and fixed process termination, not third-party patch correctness or scientific efficacy.

### Additional fail-closed regression (27 October 2026)

The action-ledger reconciler now also rejects a malformed
source-fingerprint field and overlong run identifier in a
hand-constructed structural audit. This intentionally remains
a **format check**, not cryptographic authentication: an attacker
could still supply a valid-looking but unverified SHA256 string.
[CI run 40381231237](https://github.com/Rocky5502/U-CODE/actions/runs/40381231237)
passed **621/621** offline tests on Python 3.10 and **621/621**
on Python 3.12, including the fixed first-party subprocess check.
No real-task execution, certified resource cap, or independent
measurement result is asserted by these tests.

## Next independent gates

1. Build an actually rootless, network-disabled, read-only, disposable third-party task runner only after authorized source rights and task admission.
2. Integrate a reliable run-isolated CPU/cgroup+wall meter, engine token accounting, trusted test dispatcher and GPU driver telemetry; attest and sign receipts independently of policy.
3. Bind signed receipts and process-tree caps to experiment_contract.PolicyRunReceipt and verifier authority; reject malformed or unreviewed attestations.
4. Freeze task independent hidden oracles and train-only joint-prior calibration before executing either policy. Record full attrition and all actual costs.
5. Keep the manuscript Results section empty until the independently reviewed six-checkpoint empirical study exists.

**GO** for further research engineering and source-only manuscript updates. **HOLD** for real AI-code execution and any claim of independently measured U-CODE effectiveness.
