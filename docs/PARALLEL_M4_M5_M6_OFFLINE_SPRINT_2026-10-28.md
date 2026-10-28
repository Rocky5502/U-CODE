# U-CODE parallel M4 / M5 / M6 engineering audit (28 October 2026)

**Stage:** OFFLINE PROSPECTIVE METHODS ONLY. This evidence is about
first-party code contracts, not real-world code repair or LLM performance.

## M4 — Policy fairness before running experiments

The registered confirmatory comparison requires not just equal budget
limits but shared **opportunities to create/diagnose candidates**. The
new `src/ucode/shadow_assignment_parity.py` validates a *complete*
assigned Cartesian product over tasks, model identities, seeds,
resource budgets and all eight policies. It checks exact agreement
within and across policy arms on:

- task lineage, immutable pre-fix SHA and pre-fix visible specification hash;
- model checkpoint and execution environment identity;
- public candidate archive and matched action-opportunity catalogue;
- tool access and all five initial resource caps.

Missing or duplicated arm, changed task/model/seed, mismatched common
opportunity or any single exceeded budget dimension fails closed.
A deterministic digest captures the supplied *public-only* assignment
plan. The `scripts/audit_shadow_assignment_parity.py` fixture has **one
synthetic, non-executable task, six planned model names, two illustrative
unfrozen seeds, one illustrative budget and eight registered policies**.
This produces 96 illustrative assignment rows, **not** 96 real trials.
No real task IDs, model revisions, oracle labels, source blobs or
third-party code are used. Equal asserted hashes do not prove that
separate model runs sampled the same proposals: trusted capture/replay
and independent metering remain necessary. It does not implement all
eight policies or replace the existing actual receipt/evaluator audit.

## M5 — Model and runtime cross-manifest gate

`scripts/audit_six_model_crosswalk.py` reconciles the unchanged
six-model selection, original model inventory, the planned
one-A100 AI Galaxy deployment profiles, and the unchanged eight-policy
confirmatory research protocol. It reports existing blockers rather
than downloading model weights or renting a GPU.

Special-case risks are explicit: Meta and Google model-specific access
terms; DeepSeek's potential custom model-code security review; and
Devstral's checkpoint-specific A100 precision/kernel compatibility.
Neither pre-selected model identity nor a projected memory footprint
certifies runnable weights. **All six model identities are still
prospective; zero independent task inference results exist**.
No model substitutions or policy omissions are allowed.

## M6 — Manuscript and pre-experimental question framing

The Springer manuscript `paper/overleaf/main.tex` now states
**RQ1–RQ6** and what could falsify or measure each question, including
the RQ3 paired intention-to-treat denominator, wrong-release
risk alongside release coverage, and the need for randomized RQ4
interventions. The `paper/OUTLINE.md` model-and-policy description is
updated from a stale “4–6 models” statement to the frozen six-name
planning roster and eight arms. Source-only Overleaf exports remain
subject to CI checks. This is not verified live Overleaf editing or a
compiled PDF.

## Evidence separation and blockers

1. **Task qualification:** independent as-of-task specification,
   source rights, oracle authorship and secrecy, lineage and sandbox
   approval remain unsigned/unverified. PHP #104 has a reviewer-only
   ten-family blueprint; it is NOT an executable benchmark.
2. **Computational model readiness:** immutable weights/tokenizer
   revisions, terms and runtime security checks are not approved.
   No external A100 rental has been authorized.
3. **Confirmatory experimental execution:** real matched candidate
   draws, measured five-vector receipts, complete eight-policy
   implementations and independent correctness labels are absent.
4. **Reporting:** null results and missing denominators must not be
   replaced by offline smoke test success; synthetic “trial” labels
   are explicitly excluded from RQ effectiveness numbers.

### Reproduce offline

```bash
python -m scripts.audit_shadow_assignment_parity
python -m scripts.audit_six_model_crosswalk
python -m unittest discover -s tests -v
python -m scripts.audit_overleaf_sources
```

These scripts neither launch third-party executables nor touch the
hidden evaluator. CI runs the same reference checks on Python 3.10
and 3.12.
