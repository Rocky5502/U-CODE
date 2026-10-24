# U-CODE

**Uncertainty-Guided Search for Reliable AI-Generated Software**

> Research-stage framework. No effectiveness claims, completed model experiments, or verified 120-repository corpus are asserted.

U-CODE studies **when a software engineering agent should test, retrieve context, generate another patch, repair, or abstain** under a fixed execution and inference budget. The target is the Springer *Automated Software Engineering* special issue **Search-Based Software Engineering in the Era of LLMs and Agentic Systems** (30 January 2027): https://link.springer.com/collections/jjcfecffai.

## Current status (24 October 2026, five PR screening positions per language)

- **120 discovery candidates across 12 GitHub primary-language search categories**, each with a PR link returned for `author:copilot-swe-agent[bot] is:pr is:merged`. **These are NOT 120 verified AI-generated repositories.** GitHub bot attribution alone does not establish what fraction of source code is AI-authored.
- Public dataset leads: [AIDev](https://huggingface.co/datasets/hao-li/AIDev), [SWE-chat](https://huggingface.co/datasets/SALT-NLP/SWE-chat) (gated), [DroidCollection](https://huggingface.co/datasets/project-droid/DroidCollection), [SWE-rebench](https://proceedings.mlr.press/v306/badertdinov26a.html), [EffiBench-X](https://huggingface.co/datasets/EffiBench/effibench-x). They have **distinct units of analysis** and must not be naively merged.
- **Issue #1 cumulative read-only screen:** **60/120** PRs checked: **28** production-source-path candidates, **5** test-only, **26** non-source, **1** empty file-list requiring review. **33** have recognized repository-level SPDX metadata; **6** forks; **0 fully eligible** pending independent AI-line attribution, per-file rights and safe test oracles. [Initial 24-PR evidence](docs/logs/2026-10-24_issue1_stratified_pr_audit.md) · [Third-entry screening](docs/logs/2026-10-24_issue1_second_stratified_batch.md) · [Fourth-entry screening](docs/logs/2026-10-24_issue1_fourth_stratified_batch.md) · [Fifth-entry screening](docs/logs/2026-10-24_issue1_fifth_stratified_batch.md). GitHub discovery language is not necessarily the changed-source language.
- The project initially offers a **pure-Python research scaffold** and **offline toy environment**, not a trained/calibrated uncertainty model or model-driven code repair engine.

## Research thesis

Our testable hypothesis is that **calibrated uncertainty signals, integrated into budget-constrained multi-objective search, can improve independently verified code reliability** against matched-cost baselines. Null and negative results are publishable.

## Repository contents

| Path | Purpose |
|---|---|
| `data/discovery/agent_pr_candidates_120.csv` | 120 discovery links, not vetted code |
| `data/discovery/dataset_source_registry.csv` | 10 dataset leads, all not downloaded |
| `data/discovery/pilot_pr_metadata_triage_4.jsonl` | Four real PR metadata checks; no code execution |
| `src/ucode/audit.py` | Read-only GitHub PR metadata/changed-file screening |
| `scripts/summarize_audit.py` | Deduplicated, fail-closed audit rollup from canonical JSONL |
| `src/ucode/uncertainty.py` | Probability quality, entropy, disagreement, calibration metrics |
| `src/ucode/search.py` | Explicit Pareto frontier and cost-aware intervention controller |
| `src/ucode/acquisition.py` | Monte Carlo expected hypervolume improvement per unit cost (prototype) |
| `src/ucode/simulation.py` | Deterministic *synthetic* environment for unit tests and debugging |
| `docs/RESEARCH_PROTOCOL.md` | Design, RQs, experiment matrix, rigor and leakage rules |
| `docs/DATA_GOVERNANCE.md` | Evidence and redistribution gates |
| `docs/PROJECT_BOUNDARIES.md` | Novelty and overlap safeguards |
| `paper/OUTLINE.md` | Journal manuscript blueprint, no fabricated results |
| `configs/models.json` | 6 model candidates, not downloaded |
| `tests/` | Offline tests |

## Quickstart

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
ucode simulate --seed 7
python examples/ehvi_smoke.py
ucode audit --limit 3 --output data/derived/pr_audit.jsonl
# Summarize the canonical GitHub-audited candidates and validate provenance
python -m scripts.summarize_audit --audit-dir data/audits/2026-10-24 --output data/derived/screening_summary.json
# Next *unexamined* balanced cohort: sixth entry in each of 12 query-language groups
ucode audit --per-language 1 --language-offset 5 --output data/derived/batch06.jsonl
```

The `audit` command makes **read-only** GitHub REST requests and may hit rate limits; set `GITHUB_TOKEN` in your environment for higher limits. Do not commit the token. No GitHub repository is cloned or executed by the audit command. The demo uses synthetic, explicitly labeled data; its scores are **not experimental evidence**.

See the protocol before drawing any conclusions. Code in this repository may be redistributed according to its own license; third-party code and data retain their source licenses.

## 2026-10-24 research execution snapshot

The complete GitHub-derived PR metadata with immutable SHAs is in
[data/audits/2026-10-24/](data/audits/2026-10-24/), including the
[24-record normalized manifest](data/audits/2026-10-24/stratified_24_verified_metadata_with_triage.jsonl).
The read-only audit CLI now supports deterministic query-language stratum
offsets, distinguishes production-source / test-only / non-source changes,
and halts immediately on GitHub HTTP 403/429 instead of retrying in a loop.
**Metadata approval is not dataset eligibility.** No runnable third-party
code was executed for this research block.

## Evidence and next milestones

A four-PR API metadata spot-check found two source-bearing candidates
(MLflow #27058 is a JavaScript module under a tooling directory and
forem #24047 has Ruby source/tests) and two build/CI-only candidates
(Quantinuum/zixy #270 and boot-ui #1549). These are *initial* path checks,
not completed source attribution/license/functional verification. GitHub's
API identifies the author as `Copilot`, so the auditor accepts that
confirmed API alias as well as the discovery query name.

The initial offline CI suite passed on Python 3.10 and 3.12 for
the pre-acquisition commit; subsequent commits are checked by the
same workflow. Check [Actions](https://github.com/Rocky5502/U-CODE/actions)
for the current head commit status.

Track the six research gates in [GitHub Issues](https://github.com/Rocky5502/U-CODE/issues).
No model weights or 2–5 GB repository corpus have been downloaded,
and no real model accuracy/reliability experiment is claimed.


## Research command center — 24 October 2026

- **[Principal Investigator Master Superprompt (dated)](docs/UCODE_MASTER_SUPERPROMPT_2026-10-24.md)** — all senior research roles, Mermaid dependency graph, G0–G13 gates, six RQs, multiobjective search, dataset/model matrices, 30-minute work-block checklist, and journal milestones.
- **[Execution checkpoint](docs/UCODE_EXECUTION_CHECKPOINT_2026-10-24.md)** — exact next issue, status and evidence-led session ledger.
- **[Official Springer/Overleaf LaTeX shell](paper/overleaf/main.tex)** — sn-jnl manuscript skeleton, **not submission-ready**.
- **[Overleaf setup instructions](paper/overleaf/README.md)** — use publisher class from official Springer template.
- **[Six GitHub research issues](https://github.com/Rocky5502/U-CODE/issues)** — persistent acceptance gates.

**Reminder limitation:** the 30-minute schedule is a work-session *timebox*;
a one-time reminder, if created, does not establish an always-on research agent.
Every task requires real execution evidence and a current-state check.
