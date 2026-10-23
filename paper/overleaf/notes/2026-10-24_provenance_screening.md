# Provisional manuscript evidence note — provenance screening

**Date:** 2026-10-24 · **Status:** descriptive dataset-engineering pilot ONLY

## Source and scope

U-CODE currently contains a discovery manifest of 120 GitHub repositories that
matched Copilot coding-agent PR queries in twelve GitHub repository-level language
categories. The first two PR links per discovery-language stratum were screened
via GitHub API (n=24). GitHub author names, merged flags, immutable base/head/
merge SHAs, changed-path lists, repository-level SPDX metadata and fork status
were recorded verbatim in the [audit JSONL](../../../data/audits/2026-10-24/stratified_24_verified_metadata_with_triage.jsonl).

Path-only triage of these 24 PRs identified 13 with at least one apparent
production source file, two with test-only code changes, and nine with no
eligible source-code changes (e.g. documentation, CI, assets, build metadata).
Twenty-four PRs resolved as merged and authored by API account `Copilot`.
Only twelve repositories had recognized repository-level SPDX metadata;
three were forks. All source-level licensing, independent authorship
attribution and runnable-oracle checks remain pending. Thus **zero actual
study records have passed every sample-eligibility gate**.

Three PRs have production-code language labels inconsistent with their
GitHub repository-level language search category; one additional PR is
multilingual. Language should therefore be assigned from the changed
source files and included as a multilabel variable when appropriate.

This convenience/stratified batch is not a random representative sample
of all 120 links. Do not estimate the eligible prevalence by extrapolating
13/24. The wider archive must undergo the same screening.

## Manuscript status

This evidence can support a preliminary Methods statement about *data
curation approach*, but may not support any effectiveness, calibration,
security or agent performance result. When the full cohort is screened,
regenerate the attrition table and language distribution from source
metadata and replace this interim summary.

No experiments, GPU sessions, code execution, hidden oracles, or new model
inference were performed while collecting these metadata.

**Full ledger:** [Issue 1 session report](../../../docs/logs/2026-10-24_issue1_stratified_pr_audit.md)

**Official Overleaf skeleton:** [main.tex](../main.tex)
