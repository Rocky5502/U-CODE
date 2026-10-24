# U-CODE research work block — evaluator boundary and independently defined correctness

**Date:** 2026-10-25. **Starting GitHub main:** ba086e07bcfb4e0bb3dadc0f1524195f55d0cfe1. **Starting verified test count:** 284 on Python 3.10/3.12. **Goal:** move two real pinned PR leads closer to a defensible evaluator without exposing hidden oracle information to coding policies.

## Delivered to GitHub main

1. [Evaluator boundary contract](../../src/ucode/evaluator_boundary.py): exact policy-visible metadata allowlist, evaluator-only oracle fields, blocked reused PR tests, frozen Git SHA references and declared microtask/full-PR distinction. Rejects self-declared execution eligibility, compromised source/test visibility, train/eval lineage identity, forged image digests and bad record properties. **This is not physical host or process isolation.**
2. [Two prospective registrations](../../data/evaluation/2026-10-25/prospective_oracle_registrations.jsonl) match the previously pinned PHP #104 and Go #43 dossiers. Go visibility is anchored to the immutable pre-PR design.md Git blob SHA; PHP only has a mutable issue URL with *no verified frozen specification blob*. Both explicitly have **zero oracle artifacts, zero oracle commitments, zero independent review/runner attestations**, and remain unadmitted.
3. [Offline binding verifier](../../scripts/check_evaluator_boundary.py) joins the original 120-link metadata manifest and both real task dossiers, rejects missing/duplicated records and task/changed-test drift, reports blocked preexecution status. It makes no GitHub, container, model or third-party code execution calls.
4. [Evaluator separation tests](../../tests/test_evaluator_boundary.py): 16 adversarial tests (secret ref leak, PR-authored test contamination, unpinned image, fake seal, tainted training/evaluation group, improper signer/implementer, forged SHA and omitted test lists).
5. [Analytical pre-fix oracle ambiguity reference](../../src/ucode/spec_ambiguity.py) and [12 first-party property tests](../../tests/test_spec_ambiguity.py). With two capped loser deltas (0,-5), zero sum and nonnegative balances require five recovered points, but even after an **extra hypothetical** fair near-equal constraint both winner allocations (2,3) and (3,2) remain permitted. This is an elementary **specification underdetermination witness**, NOT a demonstrated bug in the external Go PR. Exhaustive arithmetic tests operate only on a first-party model.
6. [First-party reproducible demonstration](../../examples/pilot_oracle_boundary_smoke.py) plus [three documentation-integrity tests](../../tests/test_pilot_oracle_smoke.py). CI now prints explicit pending/no external execution status.
7. [Springer LaTeX](../../paper/overleaf/main.tex) includes explicit policy/evaluator split and the nonunique settlement equation (label: eq:oracle-ambiguity). [README](../../README.md) includes links, runnable first-party demo and strict scientific limitations.
8. [Source-only Overleaf export](../../.github/workflows/ci.yml) remains active; direct authenticated Overleaf editor has not been updated. Official Springer class compilation and publisher camera-ready PDF remain unverified.

## Research findings and risks

- Evaluator gold observations must never affect action selection or patch-generation training; merely stripping JSON oracle fields is **necessary but insufficient** because untrusted source/issue text can encode answer contamination. Need audited process/filesystem/network isolation and independently reviewed task specs.
- The PHP issue URL is publicly mutable and currently has no verified pre-PR blob commitment. Using its current content as if frozen before the original agent PR would be a chronology/provenance mistake. The Go base-revision design SHA offers stronger pre-existing spec evidence but does not establish task-oracle independence.
- A changed test file and Copilot commit attribution do not make a correctness oracle or prove line-level agent authorship. All 16 original admission gates for two real PR leads are **PENDING**.
- Near-equal fairness is a **hypothesis added for the mathematical witness**, not an asserted original business requirement. Two feasible fair allocations cannot be resolved by pointing to the agent-written implementation. Full original Go settlement requires database idempotency/transaction validation as well.
- No independently approved executable task, real task run, model inference, calibration estimate or measured release-risk/success benefit has occurred. **All six user-approved model candidates remain study-planning selections only.**

## Scientific next gate

Request independent file rights and reviewer signoff; freeze the PHP pre-PR requirement snapshot (or explicitly exclude it), have an independent domain reviewer decide acceptable Go tie-break outcomes and distinct scope, design actual evaluator-only artifacts with sealed access, and audit rootless network-off resource-capped execution separately. Only when these gates are independently attested can U-CODE pursue matched-budget tests on genuine repository tasks.

**Reproduction without external code:**
- python -m scripts.check_evaluator_boundary
- python -m examples.pilot_oracle_boundary_smoke
- python -m unittest discover -s tests -v

**Engineering completion is not scientific acceptance.**
