# U-CODE — Declared frozen task/oracle identity manifest (3 November 2026)

**Scope:** offline evaluator-side consistency, not a verified pre-outcome timestamp or an attested oracle. **No real tasks were admitted; no hidden tests were created, executed, or sealed; no model inference or external repository execution took place.**

## Why an additional contract is needed

The [task-scoped oracle consistency guard](EVALUATOR_TASK_ORACLE_CONSISTENCY_2026-11-03.md) rejects oracle substitutions across observed *release verdicts* for one task. But a caller could replace **every** verdict's oracle digest together, making a fabricated or easier evaluator self-consistent. Worse, a task with no releases has no verdict from which to infer the oracle was preselected.

A confirmatory experiment must freeze the task-to-hidden-oracle correspondence *independently of outcomes*, before any policy run. The design cannot use a dictionary built post hoc from the same verdicts it is auditing.

## Implemented in first-party code

- `src/ucode/frozen_oracle_contract.py`: bounded immutable `FrozenOracleManifest` with one lowercase SHA256 digest per task. Rejects duplicate tasks, mutable nested entries, invalid identifiers, malformed digests and any claim of independently authenticated status.
- `audit_confirmatory_run_matrix(..., frozen_oracles=manifest)`: opt-in evaluator-side binding against this separate input. Requires **every** assigned task to appear exactly once, including tasks where all arms abstain or fail, and rejects any released patch evaluated with a digest different from that task's declaration.
- `paired_effect_attrition_bounds` and `postterminal_contrast` forward the frozen declaration to the same validator.
- New adversarial tests demonstrate a *uniform* post-hoc oracle switch that passes ordinary within-batch consistency but fails against the separately provided declaration, missing/extra task entries, all-abstain coverage, malformed manifests and failed propagation into final paired metrics.
- `CompleteStudyAudit.declared_frozen_oracle_bindings_match` is only a **structural equality flag**. `independently_authenticated_oracles` explicitly remains **False**.

The parameter is optional for backward-compatible first-party mathematical fixtures. For a future approved real experiment, pass a separately protected manifest and require `declared_frozen_oracle_bindings_match=True` as **one necessary check**, not as proof of approval.

## What this still cannot do

**The code does not prove the manifest was truly frozen before evaluation.** A caller who invents both a fake manifest and fake verdicts can still achieve equality. Actual research acceptance requires:

1. Independent, evaluator-controlled creation of task-specific functional tests, separate from PR-authored tests and all policy/model outputs;
2. Authenticated pre-outcome commitment to the evaluator's hidden oracle artifact digest, anchored to the immutable task base, spec, split and toolchain, with trusted timestamps or verifiable signed evidence;
3. Reviewer verification of task specification, author independence, file-level reuse rights and accepted behavior (especially the Go odd-remainder ambiguity);
4. Physical policy/evaluator isolation, locked source and dependency provenance, and independently enforced five-resource metering;
5. Detection/reporting of nondeterministic or flaky tests under a separate predeclared repeated-trial design.

Only after these gates can a deterministic structural comparison become part of a scientifically admissible evaluation. **Two pilot dossiers remain pending all 16 admission gates.** The source-only manifest must not be sent to the runtime policy or stored with the public task prompt if it reveals hidden evaluator material.

## Reproduce

```bash
python -m unittest discover -s tests -p 'test_frozen_oracle_contract.py' -v
python -m unittest discover -s tests -p 'test_experiment_contract.py' -v
python -m unittest discover -s tests -v
```

See [issue #7](https://github.com/Rocky5502/U-CODE/issues/7) and the [current status report](UCODE_RESEARCH_PROGRESS_2026-11-03.md). The primary study RQs, eight policy IDs, six model IDs and zero-result status are unchanged.
