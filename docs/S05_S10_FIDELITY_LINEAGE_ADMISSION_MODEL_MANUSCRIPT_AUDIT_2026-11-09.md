# U-CODE S05–S10: six-stage source-integrity audit and independent evidence handoffs

**Date: 9 November 2026. Scope: read-only first-party research engineering, no executable third-party code or model inference.**

This consolidates [S05 #65](https://github.com/Rocky5502/U-CODE/issues/65), [S06 #66](https://github.com/Rocky5502/U-CODE/issues/66), [S07 #67](https://github.com/Rocky5502/U-CODE/issues/67), [S08 #68](https://github.com/Rocky5502/U-CODE/issues/68), [S09 #69](https://github.com/Rocky5502/U-CODE/issues/69) and [S10 #70](https://github.com/Rocky5502/U-CODE/issues/70). It distinguishes **work completed in source code** from **scientific milestones blocked on independent evidence**. No “five hours nonstop” background session or half-hour automation is claimed.

## S05 — Eight-policy comparator fidelity audit

The frozen six-model/eight-policy protocol fixes the treatment `ucode_conditional_bes` versus primary comparator `no_uncertainty_search`. The [shadow eight-arm runner](../src/ucode/shadow_eight_arm_runner.py) previously already declared **eight callback slots, not eight faithful baseline implementations**. It now also exposes the number of **distinct handler factory objects** and groups of **aliased factory registrations**, so the all-eight-using-one-callback smoke test cannot be mistaken for eight algorithms. Distinct factories still **do not** certify behavior, academic source-method fidelity, matched opportunities, budget parity or hidden-oracle independence.

The new [six-stage cross-ledger audit](../src/ucode/remaining_stage_evidence.py) carries an eight-row concrete research-method fidelity gap register. Required future comparator validation includes: source methodology and citation review; source-to-adapter test vectors; treatment-independent common task/seed/model/initial proposals; exact five-cap opportunity parity; true algorithmic MCTS rollouts/backups (not a renamed greedy search); fixed testing commitment; and comparator-specific verification rules. The external RETRACE-style, Dockerless-style and SWE-Verifier-style methods are **planned** external comparators, not additional independently reproduced study arms. **Confirmed faithful comparators: zero**.

## S06 — 120-PR lineage contamination and split integrity

The existing [lineage risk graph](../src/ucode/lineage_risk_graph.py) produces conservative **potential** edges from fork/commit hints and owner-only warnings. No metadata edge proves that two actual code tasks are duplicates; the graph cannot grant a train/test split.

The [lineage bundle verifier](../src/ucode/lineage_graph_verify.py) now checks **semantic invariants even when an adversary rewrites BOTH exported CSV files and their own SHA256 digest manifest**. It requires exactly 120 unique candidate IDs; valid file schema; component label sizes matching actual members; valid oriented endpoints; unique edge tuples; strict relation types, caution labels and per-relation summary counts; and that strong provenance edges connect records inside the **same** proposed component. Owner-only edges must retain their warning treatment. The synthetic [S06 tampering tests](../tests/test_lineage_graph_semantic_integrity_s06.py) falsify forged self-rehashed edits. These are **first-party consistency checks**, not independent Git ancestry verification, uncontaminated evaluation partition or task admission. **Independently frozen lineage split: none**.

## S07 — Go #43 source-era microtask independent adjudication

Canonical [Go #43 blueprint](../data/admission/2026-11-07/go43_pre_fix_oracle_review_blueprint_PUBLIC_NO_GOLD.json) retains **12 public question families**, **six unresolved normative ambiguities**, independently recorded original source-era commit/blob identifiers and **no expected gold values**. The pre-fix document/source rules have not been privately and independently adjudicated. In particular, zero-floor versus conservation, fractional multipliers, team/player splits, higher-priority business-rule source, and retry/atomicity semantics require an accountable human specification owner.

The cross-ledger audit checks the pinned base against the pilot registration, all six original question states, no gold outputs, and the unchanged **8/8 independent admission gates pending**. It refuses forged `task_admitted`, `go_executed` or `oracle_sealed` flags. Do not reveal any future evaluator-only gold answer to the agent or treat PR-authored tests as independent. **Outcome: public handoff source checked, external human signoff blocked**.

## S08 — PHP #104 source-era rights/specification review

The [PHP #104 blueprint](../data/admission/2026-10-28/php104_oracle_review_blueprint_PUBLIC_NO_GOLD.json) specifies **10 public case families** with no oracle output, immutable pre-fix file pointers and a published root-license *lead*, not rights clearance. The parent issue's exact text **at PR creation time** remains unsealed; a present-day issue view does not solve the version/chronology question. Original source file permission, developer authorship and a separately drafted hidden oracle still need independent approval.

The cross-ledger audit checks the pilot base SHA against the blueprint, all nine explicit no-approval/no-execution flags, no gold case values, and **8/8 external gates pending**. **Outcome: scope and rights handoff source checked, external human signoff blocked**.

## S09 — Six exact model identities and public Hub metadata

The [public six-model card audit](P0_3_PUBLIC_SIX_MODEL_CARD_AUDIT_2026-11-09.md) remains observational metadata **only**. Every model still requires an independently authenticated immutable weight/tokenizer source revision, byte integrity, complete version-specific license/terms determination, approved use/access (including gated models), frozen engine/precision/chat-template versions, physical VRAM and five-resource meter observations on an isolated host. A public 40-character Git SHA or Hub label is not itself a checkpoint approval. The DeepSeek public `other` label versus historical planning `deepseek-license` label is a **metadata taxonomy discrepancy**, not legally adjudicated license drift.

The source [cross-ledger audit](../src/ucode/remaining_stage_evidence.py) checks all six model IDs against the canonical protocol; zero approved checkpoint snapshots, zero independently confirmed rights reviews, zero private gated account approvals, zero loaded/inferred model tasks and explicit `model_runnable_for_study=false` on every public card. **Outcome: provenance-gaps audited; actual runner qualification blocked, 0/6 checkpoints**.

## S10 — Springer paper and replication consistency

The [GitHub manuscript source](../paper/overleaf/main.tex) carries prospective matched ITT, leave-one-lineage-out, missingness sign sensitivity, six-objective matched resource hypervolume and S04 conditional likelihood coherence. These are **source methods**, not published findings. The [cross-ledger tool](../scripts/audit_remaining_sprint.py) checks for their source markers and cross-validates **zero independently qualified major scientific exit criteria**, **no measured primary effect**, **no independently compiled publisher PDF**, and **no confirmed live Overleaf synchronization**.

U-CODE's Springer *Automated Software Engineering* special-issue deadline is registered as **30 January 2027** (not independently reverified by this offline audit). Manuscript submission-readiness is still blocked on an approved executable cohort, source-era rights, independent hidden oracle, secure isolation, six qualified model runtimes, faithful comparators, validated train/test lineage split, measured paired results and uncertainty estimates. **Outcome: manuscript source status audited; fully empirical paper not yet complete**.

## Reproduce the offline, source-only verification

```bash
python -m unittest discover -s tests -p 'test_shadow_eight_arm_runner.py' -v
python -m unittest discover -s tests -p 'test_lineage_graph_semantic_integrity_s06.py' -v
python -m unittest discover -s tests -p 'test_remaining_stage_evidence.py' -v
python -m scripts.audit_remaining_sprint --output dist/ucode-S05-S10-SOURCE-NO-RESULTS.json

# Should always exit 2 while independent permissions and results are absent.
python -m scripts.audit_remaining_sprint --require-real-ready
python -m unittest discover -s tests -v
```

A successful source-only command means **the registries are mutually consistent** and the current approval gaps remain explicit. It never issues execution permission. The `--require-real-ready` option is a **negative CI safeguard**: expected exit status is 2, not a successful trial.

**Definitions:** “source-engineering checked” means first-party code and tests passed; “external scientific exit verified” requires independent rights, provenance, evaluator, hardware and outcome evidence. This report does not satisfy or estimate the time remaining for the latter.
