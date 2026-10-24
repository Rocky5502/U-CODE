# U-CODE — Complete 120-link read-only PR discovery screen (2026-10-25)

**Research gate:** G2 candidate metadata triage is now **COMPLETE for the frozen 120-link discovery manifest**. This does not complete task eligibility, AI-authorship attribution, secure execution, source-file rights, or independent correctness evaluation. Issues #1/#2 remain open.

## Dataset, method, and provenance

- The immutable [120-link discovery list](../../data/discovery/agent_pr_candidates_120.csv) contains ten bot-author-associated, merged PR links from each of twelve *repository-primary-language search strata* (GitHub query `author:copilot-swe-agent[bot] is:pr is:merged`).
- Over 24–25 October 2026, read-only connected GitHub API actions attempted **all 120**, reading PR base/head/merge identifiers, changed filenames, declared GitHub PR account, merged state, repository-level SPDX/fork metadata, and PR size where available.
- Deduplicated canonical JSONL is stored in [data/audits/2026-10-24](../../data/audits/2026-10-24/) (the original audit folder is retained for reproducible inclusion). The newly completed eighth, ninth, and tenth per-stratum positions are `stratified_offset7_ids*.jsonl`, `stratified_offset8_ids*.jsonl`, and `stratified_offset9_ids*.jsonl`, respectively. Although their folder retains the frozen original discovery date, new records have `audited_on: 2026-10-25`.
- The standard-library-only canonical summarizer [scripts/summarize_audit.py](../../scripts/summarize_audit.py) recomputes the attrition totals from the actual source records with no downloads/third-party execution. Newly added [tests/test_audit_120_complete.py](../../tests/test_audit_120_complete.py) asserts every ID 1–120 is represented exactly once and every language has ten entries.

## Completed metadata counts — **real observations, NOT task correctness**

| Class | PR count | Scientific interpretation |
|---|---:|---|
| Production-source **paths** detected | **62** | Path/suffix hints only; includes possible generated, moved, data-only or mixed-authorship source |
| Test-only source changed | **10** | No detected production-source path in PR |
| Non-source changed | **45** | Docs/CI/config/other changes under conservative source filtering |
| Changed-file list empty | **2** | No usable changed-file metadata; further manual research needed |
| PR inaccessible / retrieval failure | **1** | ID **26** returned GitHub 404 |
| **Total attempted** | **120** | All manifest links accounted |
| **PR metadata retrieved** | **119** | 120 attempts minus the inaccessible ID 26 |
| **Fully AI-line-attributed, rights-cleared, independently oracle-qualified tasks** | **0** | **Not a 120-task AI-written software benchmark** |

Additional descriptive metadata for the 119 retrieved PRs: **62** had recognized repository-level SPDX metadata; **57** were unknown or `NOASSERTION`; **12** records were forks. Repository-license metadata does **not** establish file-level reuse permission or the license of modified third-party code. An observed merged PR does **not** establish functionally correct software.

**Denominators matter.** The original 24, later 84, and new full 120 attempts are successive *cumulative metadata screens* of the same frozen list. Older README/issue summaries are historical interim checkpoints and are not independent study cohorts. Today's reported 62 source-path hits are **not** 62 agent-generated patches, and 119 retrievable links are **not** 119 independently tested software programs.

## Selection of the next human verification queue

The newly introduced [review_queue.py](../../src/ucode/review_queue.py) and [offline queue CLI](../../scripts/triage_review_queue.py) reproduce a deterministic **MANUAL_REVIEW_ONLY** shortlist. They prioritize a source-bearing PR when the observed changed-file list is small, accompanying tests are present, repository-level SPDX is recognizable, no fork is detected, and the path heuristics do not reveal obvious security-sensitive/generated/data-only content. These are **triage heuristics**, neither eligibility criteria nor a validated source-authorship classifier. All 62 hits remain `eligible=FALSE`, pending provenance and rights reviews.

Initial CI output for the complete ledger identified **14** source/test/license/path-compatible *first-pass manual-review leads*. That only means there is a plausible place to start a human rights-and-oracle audit, not that 14 experiments are runnable. In particular:
- Some source paths (e.g. C# word lists or package distribution scripts) are not meaningful bug-fix implementations despite their language suffix.
- Some source-bearing PRs are security-sensitive (auth/SAML), bulk refactorings or generated caches. These need stricter review and are not automatically pilot tasks.
- The original 24 JSONL rows did not include a standalone `test_files` list. CI caught this schema difference, and the prioritizer now reconstructs **only conservative test-path hints from the immutable recorded changed filenames**. A missing path list fails closed rather than fabricating tests.
- Do not use GitHub's `PR author: Copilot` to assert the share of autonomously generated changed lines. A separate immutable two-PR commit/co-author audit already demonstrates mixed human--AI metadata patterns.

## Reproduction without third-party execution

```bash
python -m scripts.summarize_audit --audit-dir data/audits/2026-10-24 --manifest data/discovery/agent_pr_candidates_120.csv
python -m scripts.triage_review_queue --limit 12
python -m unittest discover -s tests -v
```

GitHub-hosted CI runs only U-CODE first-party standard-library test and metadata code. It **does not clone or execute any source from the 120 external PR repositories**. The checker does not verify live repository licenses, upstream authorship, test quality, or safe sandbox isolation.

## Manuscript updates

The prospective Springer [main.tex](../../paper/overleaf/main.tex) now contains a citation-independent description of the completed frozen discovery method and **real descriptive attrition table** labelled `tab:pr-screen`. This is exploratory **metadata** evidence, not an effectiveness result, not RQ1–RQ6 verified task outcomes, and not statistical evidence for improved search/release policies. The Results section still has no independently verified model task-success comparisons. No live Overleaf editor was synced; GitHub's CI exports the source-only LaTeX/BibTeX bundle.

## Highest-value next scientific gates

1. **Task selection:** human-assess first-pass queue commits/changed production files, authorship traces, complete file-level rights and realistic executable pre-fix restoration. Document exclusion reasons and coverage at each gate. Reconfirm repo licenses and code data provenance at immutable revisions.
2. **Sealed oracles:** select tasks whose correctness can be independently evaluated, with tests unseen by generator, search or risk estimator. Use a genuinely isolated disposable rootless/no-network/resource-limited runner, not GitHub CI.
3. **Real model feasibility:** preserve the six user-selected checkpoints in the study plan, review gated provider terms, pin actual checkpoint/tokenizer revisions, audit appropriate inference engines, and measure memory before any resource purchase or claim of inference.
4. **Real controlled pilot:** record pre-outcome diagnostic panels and independent correctness outcomes, fit separate success priors and conditional diagnostic models on train groups only, and compare U-CODE/BES versus no-uncertainty search and selective verification under matched five-vector budgets.

**Scientific posture:** G2 discovery metadata screen complete (120/120 attempts). **Dataset eligible 0; verified LLM experiments 0; real search reliability gain unmeasured.**
