# Data Descriptor outline (NOT SUBMISSION READY)

**Working title:** *A provenance-audited multilingual discovery inventory of
AI-associated software pull requests*

**Intended venue (separate from ASE):** Scientific Data, Data Descriptor
**Status:** proposal for a future **substantially enriched and independently
validated** dataset version, not an assertion of current suitability.
**Do not submit this outline as an empirical journal article.**

## Background & Summary

AI-associated pull request records are increasingly used as proxies for
real repository-level coding tasks. A public PR's bot account,
merged status, root license, and changed file paths do not verify whether
a patch was autonomously authored, legally reusable or independently
functionally correct. A reusable data resource could separate discovery
metadata, code provenance, functional specification, independent held-out
oracle checks and repository-family leakage groups. The present U-CODE
resource offers only the first **metadata screening** layer.

## Methods — INPUT DATA and record acquisition

The source snapshot comprises 120 GitHub PR URLs from 12
GitHub query-language strata (10 per stratum), from
\`author:copilot-swe-agent[bot] is:pr is:merged language:<stratum>\`
searches recorded 24 October 2026. The independent query-language
label is **not** a confirmed changed-file language or line-level AI label.
The full unedited source manifest and timestamped read-only audit
JSONLs must be archived as review inputs. One PR metadata retrieval
failed; it remains represented as a missing source record.

Describe in the future submission every API endpoint, pinned revision,
metadata field, extraction date, rate limit and transformation rule.
Do not infer task suitability from search rank or cherry-picked
promising PRs.

## Methods — data transformation and eligibility

Current standardized curation is deterministic:
\`scripts/audit_dataset_quality.py\` performs strict joins,
source/test path classification, duplicate and mismatch checking,
ten-link search-stratum preservation, rights and sealed-oracle
blocking, and portable source/output SHA256 inventory.
It outputs one **metadata** row per discovered PR, a
12-language stratum summary, a manual-review subset and QC files.

Full task data construction remains **unperformed**.
The next validated release would require independent pre-fix
task statements, developer environment, reproducible build/test
commands, code rights, verified modified-line authorship,
and an evaluator-only held-out functional oracle, with measured
inter-annotator agreement and adjudication. No such labels can be
invented from PR metadata, code comments or merged status.

## Data Records (present versus proposed)

**Present: metadata release (8 compact files)**

- \`clean_metadata_120.csv\` — unique discovery PRs, search stratum,
  changed production-language hints, source/test path counts,
  immutable PR SHAs where retrieved, and pending review flags.
- \`language_strata.csv\` — per-query-language counts.
- \`manual_review_12_NOT_EXECUTABLE.csv\` — work queue only.
- \`cleaning_report.json\` — attrition counters and source SHA.
- \`dataset_schema.json\` — field dictionary, restricted-use notes.
- \`quality_report.json\` — completeness, structural checks, flags.
- \`manual_lineage_and_rights_flags.json\` — warning-only per-record flags.
- \`release_integrity.json\` — SHA256 of inputs and seven outputs.

**Proposed, absent:** a file-level rights manifest;
independently annotated pre-fix task JSONL; container/toolchain
digest records; independent oracle specification and authenticated
test receipts; verified task-family splits; coder/annotator agreement
records; versioned leakage screening; preserved allowed source
snapshots; independent hardware/metering provenance. No estimate of
this missing dataset's final task count is currently justified.

## Data Overview (optional and brief)

Present metadata contains 120 distinct repository names / PR links.
Of 120 links, 119 returned PR metadata and 62 exhibited production
source-path signals. Fourteen were first-pass screening priorities
and 12 joined a diversity-aware **manual** review shortlist.
The 12 label strata are search categories; there are 11 mismatched
or unobserved changed-production-language leads among the 62.
Zero tasks passed independent executable evaluation admission.
The full 12-stratum table lives in the ASE manuscript and
\`data/curated/2026-10-27/frozen_cleaning_summary.json\`.

## Technical Validation

**Completed offline structural software checks:** uniqueness
and exact input joins, full-denominator retention, immutable
raw-to-clean revision matching, field types, leakage/privilege
flags, provenance hash receipts, and re-generation in two Python
versions by GitHub CI. Preserve the CI SHA and artifact digest.

**Missing empirical validation:** independent task reconstruction;
benchmark oracle agreement, corrected difficulty spectrum, coverage
and attrition across *actual* changed languages; security/license
adjudication; repeat runs in pinned containers; train/test overlap
scanning over allowed source content; blind rater agreement.
It is scientifically improper to describe the current
version as an independently executable benchmark.

## Usage Notes

- Use current data only to study source selection, read-only
  repository/PR metadata and methodological issues in dataset
  construction. Do not use as full task-success labels.
- Do not feed post-PR head/merge or PR-created tests to an agent
  asked to fix a pre-PR task: this leaks the outcome.
- Do not split random PR rows into train/test without independent
  repository-family and duplicated-task adjudication.
- Do not redistribute third-party source, binaries, patched test
  assets or model weights without appropriate licensing.

## Data availability

**Current:** GitHub U-CODE source repository plus CI metadata artifact.
**Missing for Data Descriptor submission:** a static, deposited,
reviewer-accessible, eventually publicly archived data version in
a suitable recognized repository with permanent citation DOI and
machine-readable licenses. No DOI has been minted.

## Code availability

Rebuild source:
\`src/ucode/dataset_curation.py\`,
\`src/ucode/dataset_quality.py\`,
\`scripts/build_clean_pr_dataset.py\`,
\`scripts/audit_dataset_quality.py\`.
The scripts run offline with the Python standard library and
produce reproducible output file hashes; the code itself has
not undergone a separate external audit.

## Roles, ethics and competing interests

List only actual investigators, their real contributions,
licenses and conflicts after author review. Do not fabricate
independent annotators, ethical clearance, signed audits or
reviewer names.

**Submission decision: HOLD.** Scientific Data peer review
evaluates dataset quality, reuse and complete technical validation.
An interim 120-row metadata screen may be useful to disclose,
but the ambitious multilingual task benchmark and independent
oracle quality evidence have not yet been created. A prior ASE
disclosure, dataset identity or DOI can affect the value and
eligibility of a later related Data Descriptor; assess overlap
under the publisher's related-publications policy.

References: https://www.nature.com/sdata/submission-guidelines
and https://www.nature.com/sdata/policies/for-referees
