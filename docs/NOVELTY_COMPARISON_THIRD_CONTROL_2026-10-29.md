# U-CODE — defensible literature positioning and third reference control

**Date:** 29 October 2026. **Evidence status:** source-level scholarly positioning and **synthetic/offline** research-engineering, NOT measured real-task effectiveness.

## A. Manuscript: cited feature comparison, not a leaderboard

The canonical Springer source `paper/overleaf/main.tex` now contains
Table `tab:prior-method-positioning` under Related Work. It uses
printer-friendly tick/cross symbols in seven source-cited rows:

1. SWE-Search (ICLR 2025): MCTS-based agent exploration and refinement.
2. GA4GC (SSBSE 2025): multi-objective search over agent configurations.
3. SWE-Replay (2026 preprint): trajectory re-use for test-time scaling.
4. SWE-Verifier (October 2026 preprint): selective verification of sampled proposed actions.
5. PATSSEL (EMNLP Findings 2026): test-guided debug-versus-regenerate selection.
6. RETRACE (2026 preprint): training-free independent patch verification.
7. Dockerless (EMNLP 2026): environment-free patch verification.

All seven are **cited in the table** by primary-source BibTeX entries already
present in `paper/overleaf/references.bib`. Each row distinguishes
*method focus* from *empirical software-task evaluation*. The user-requested
cross marks **do not prove a feature is impossible or absent from any
implementation**: a cross only means the paper did not establish that
feature as a core contribution. The U-CODE method ticks carry a dagger
because they describe existing first-party offline references and intended
integrations, not completed real agent trials. The U-CODE empirical
evaluation cell is crossed until a held-out, independently verified
comparison exists.

The suggested novelty is joint, history-conditioned allocation between
candidate-changing actions and diagnostic evidence with explicit
cross-patch dependence and five hard budget dimensions. **This remains
a hypothesis; no comparative superiority is claimed.** See the cited
related-work section and `docs/UCODE_NOVELTY_FALSIFIERS_AND_MATHEMATICS_2026-10-27.md`
for falsifiers and prior-work overlap.

`scripts/audit_overleaf_sources.py` and
`tests/test_comparison_table_integrity.py` enforce the presence
of all original citations, the U-CODE planning symbols, and the
missing empirical-results indicator. This is structural source lint,
NOT a full paper-review or a compiled Springer PDF check.

## B. Next research task: a third synthetic adaptive controller

The source-only reference `src/ucode/uncertainty_only_reference.py`
adds an explicitly assumed, *uncalibrated* prior risk and public binary-test
likelihood to the existing
`src/ucode/adaptive_reference_replay.py` control menu.

It selects one affordable first generator, then:

- releases without extra evidence if a **frozen hypothetical** prior
  meets the predeclared predicted-acceptability threshold;
- otherwise purchases one public test if available;
- updates the stipulated prior using the public test sign and
  frozen sensitivity/specificity; and
- releases only when the stipulated posterior meets the threshold,
  otherwise abstains. It never optimizes or repairs the patch.

The rule cannot read hidden correctness labels. No second diagnostic
is presumed conditionally independent. The offline engine preserves
candidate-bound action IDs and exact five-vector accounting.
Missing risk cards, public frozen responses, invalid probabilities,
budget exhaustion and unexpected fields fail closed. The two older
local references, `fixed_testing` and `no_uncertainty_search`, may
NOT consume the synthetic confidence register.

This is a third **scoped local reference**, not the fully learned or
calibrated `uncertainty_only` comparator required for confirmatory RQ3.
It is not an original theorem or a result that uncertainty is beneficial.
All eight registered arms remain prospective and unchanged.

### Offline reproduction

```bash
python -m scripts.audit_overleaf_sources
python -m scripts.smoke_uncertainty_only_reference
python -m unittest discover -s tests -v
```

The CI smoke runs on Python 3.10/3.12 and uses fabricated public
positive/negative test signs with the same hypothetical prior.
Neither smoke case is a ground-truth correctness verdict.

## C. Genuine next P0 work

**Still zero independently admitted executable tasks and zero sealed
oracles.** Prioritize external pre-fix specification/rights adjudication
for PHP #104 or a separately labeled prospective repair task, followed
by secure rootless, networkless source execution and independently
attested five-dimensional metering. Freeze model revisions/terms and
run the first truly measured, evaluator-blind pilot only after those
gates. This comparison table does not substitute for experiments.

**Overleaf update boundary:** The version-controlled source was edited
in the GitHub `paper/overleaf` directory. CI can produce a source-only
ZIP. This sprint did **not** synchronize a live Overleaf project or
compile/inspect an official Springer `sn-jnl` PDF.
