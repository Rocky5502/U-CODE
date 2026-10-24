# U-CODE — First real-task admission research block

**Date:** 2026-10-25. **Opening checkpoint:** 9396227ec0bedfbf8f7bfca0528af54b0057c138, with 265 offline tests passing. **Goal:** advance two true public PRs toward safely executable scientific tasks without misrepresenting admission.

## Actual read-only research

We inspected official GitHub issues, immutable pre-fix repository documents, original PR diffs, changed tests, Copilot and human co-author metadata, root license blobs and relevant toolchain metadata for [PHP spider #172](https://github.com/mvdbos/php-spider/pull/172) and [Go game settlement #30](https://github.com/PlayHuai/eighty-point-huai-an/pull/30). Neither repository source was downloaded into an execution runner or run.

PHP issue #168 predated the corresponding PR by about 2 minutes 32 seconds and describes file path compatibility, encoded names and persistence/cache invariants. The pre-fix Composer manifest advertises PHP >=8.2, extensions and PHPUnit 11 development dependencies. PR tests are authored with the candidate code, not evaluator-held-out.

Go issue #29 predated the PR by eight seconds. Unlike that brief issue, the pre-fix design document supplies detailed score tiers and rank thresholds. The patch modifies scoring, DB settlement, balance capping, ranks and tests. **Key scientific ambiguity:** pre-fix requirements ask for no negative loser balances and zero-sum payouts but do not independently fix the winner of an indivisible odd remainder. The implementation chooses a deterministic tie-break; treating that choice as evaluator gold would create a circular oracle. This is not a confirmed code defect.

Both projects have root MIT LICENSE files but file-specific rights remain unapproved. Bot commit authors with human co-author trailers do not determine AI line ownership. No independent oracle, sealed evaluation, pinned/approved sandbox or verified model runs exist.

## Committed outputs

- [Eight-gate admission model](../../src/ucode/task_admission.py): immutable pre-fix task, line-level attribution, file rights, independent functional oracle, oracle secrecy, sandbox isolation, reproducible toolchain, resource limits. Fails closed for invalid path/commit/gate; even complete self-reported evidence requires external adjudication.
- [Two real immutable task dossiers](../../data/admission/2026-10-25/pilot_dossiers.jsonl): source/test paths and base/head/merge SHAs; **16 of 16 gates PENDING**.
- [First-party offline dossier verifier](../../scripts/check_task_admission.py) reconciles each record against the 120-link PR audit and never approves execution.
- [Adversarial dossier tests](../../tests/test_task_admission.py) plus [paper/README integrity checks](../../tests/test_task_admission_paper.py).
- [Research memo with original pre-PR evidence](../PILOT_ADMISSION_EVIDENCE_GATE_2026-10-25.md) and [prospective Springer main.tex](../../paper/overleaf/main.tex) updated.
- [Issue #7: independently qualified pilot](https://github.com/Rocky5502/U-CODE/issues/7), with explicit evidence acceptance checklist.
- CI runs the offline admission validator; existing source-only Overleaf export continues. No authenticated live Overleaf edit is implied.

## Scientific status

Metadata screening 120/120 complete; source-path leads 62; first-pass human review candidates 14; actual pinned admission dossiers 2; **independently admitted executable tasks 0; real six-model code-task results 0**. Development is real but cannot be reported as effective coding search or a statistical risk certificate.

**Next gate:** independent file-specific legal/provenance and task specification review, construct and seal independently authored test oracles, pin transitive dependencies, approve and attest disposable rootless network-off resource-capped runner, then perform the first measured task run with no oracle leakage into the agent.
