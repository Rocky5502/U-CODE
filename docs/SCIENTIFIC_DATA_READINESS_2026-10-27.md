# U-CODE Data Descriptor readiness and independent-validation roadmap

**Date:** 27 October 2026. **Actual publication status:** **NOT READY**.
This is a scientific quality plan, not a Nature submission or an assertion that
metadata curation alone yields an AlphaCode-comparable repair benchmark.

## Target distinction

U-CODE's **ASE** paper studies Bayesian evidence acquisition in software
agents, with the primary endpoint a *verified full task success under matched
budgets*. The separate **Scientific Data** route would be a **Data Descriptor**
about a curated, useful, versioned and technically validated data resource.
It is not another journal to submit ASE effectiveness claims.

Official guide:
https://www.nature.com/sdata/submission-guidelines

Official data policies:
https://www.nature.com/sdata/policies/data-policies

Formal review criteria:
https://www.nature.com/sdata/policies/for-referees

A Data Descriptor requires inspectable/accessible deposited data,
fully described creation and transformation methods, Data Records,
Technical Validation, a Data Availability and a Code Availability statement.
The reviewed final dataset version should be archived in a recognized
repository with permanent citation/DOI, rights as applicable.
**This GitHub metadata and Actions ZIP are not a deposited DOI or
independent evidence of complete executable tasks**.

## What really exists in this snapshot

- 120 unique repository names/PR links, 12 GitHub search strata (10 each).
- 119 PR metadata retrievals, 1 failed; 62 production-source-path leads.
- 14 high-priority metadata leads; 12 diverse candidates queued for
  **manual screening**, not valid paired tasks.
- 11 of 62 leads have a queried-vs-observed production-language mismatch
  or unavailable language observation.
- 0 independently admitted executable tasks; 0 independently sealed
  functional oracles; 0 train/validation/test repository-family assignments.
- 0 run trials on the frozen six-model matrix. Model weights/license/engines
  and full five-resource attested runtime remain pending.

All source files and code are in GitHub and the dataset is **compact**
because the eight-file release is only PR metadata + QC tables, schemas,
review flags and SHA256 receipts, not source snapshots or test fixtures.
A PR link does not confer permission to copy a changed file.

## Technical validation and reproducibility completed in software

Run:

    python -m scripts.audit_dataset_quality \
        --output-dir dist/ucode-pr-metadata-clean

This deterministic **standard-library** pipeline:

- Validates 120/120 one-to-one raw-to-clean ID and URL joins,
  unique repo/PR keys, twelve ten-link search strata, accepted
  triage states and complete attrition denominators.
- Checks exact immutable pre-fix/head/merge SHA fidelity with the
  raw audited metadata (not merely 40-hex syntax), valid source
  language labels, source file counts and no evaluator/gold data fields.
- Emits missing-cell, owner-shared, fork-parent and shared-commit
  **human-review warnings**. They are potential lineage overlap,
  not verified duplicate source-content clusters. No one may call
  the pending group hints a frozen leakage-safe train/test split.
- Rejects forged rights/attribution/oracle/sandbox flags and any
  declaration that this unqualified metadata contains executable tasks.
- Emits a machine-readable schema and explicit use restrictions,
  QC status with BLOCKED train/test/runner checks, PR flags,
  source SHA256 provenance and deterministic output file sizes/hashes.
- No external network call, third-party code, model, paid GPU,
  hidden evaluator or unapproved dataset was executed.

The release artifact contains eight text files:

1. \`clean_metadata_120.csv\`
2. \`language_strata.csv\`
3. \`manual_review_12_NOT_EXECUTABLE.csv\`
4. \`cleaning_report.json\`
5. \`dataset_schema.json\`
6. \`quality_report.json\`
7. \`manual_lineage_and_rights_flags.json\`
8. \`release_integrity.json\`

The last file hashes the other seven outputs and lists source-file hashes
under portable **repository-relative** paths. Verify raw snapshots and
all output hashes after download, and preserve the exact Git commit.

## For stronger scientific credibility: required NEW evidence

**Gate A: independent source-provenance review.** Per PR, two human
annotators inspect pre-fix specifications, bot/human commits, patch
authorship and file-level licenses. Record adjudicator IDs and
disagreement resolution. Never treat PR account as per-line provenance.

**Gate B: independent task reconstruction.** Rebuild the exact
pre-PR task from pre-existing (not patch-written) issue/specifications
with immutable base, dependencies, network requirements, and explicit
expected behavior. Reject unbuildable tasks rather than invent labels.

**Gate C: independent executable correctness oracle.** Separate
reviewers construct hidden tests independently of PR-added tests and
model outputs. Include negative controls, regression checks, leakage
screening and sandboxed repetition. Do not infer "correct" from
merged PR status or from patch tests.

**Gate D: third-party execution rights and safety.** A privileged,
rootless, network-disabled, allowlisted, independently metered
container runner must be reviewed *before* executing unknown code;
CPU/GPU/test/token/wall budgets must be enforced, not self-reported.

**Gate E: leakage-free versions and splits.** Review forks, common
owners, duplicate patches, shared issues and upstream/downstream
repository lineage. Assign train/calibration/test by adjudicated
repository-family and issue/task relationships with no oracle leakage.
No automatic random PR row split.

**Gate F: reproducible sample design and coverage.** Quantify actual
task coverage by **changed production-source language**, repository
family, complexity, test availability and successful isolated rebuild.
Predefine power/sensitivity and missingness reports; 12 language
query labels do not imply a balanced 12-language software benchmark.
A dataset that cannot support all languages may still make a valid
narrower, explicitly declared contribution.

**Gate G: archive and license documentation.** Deposited, citation-ready
immutable release on Zenodo/Figshare or other appropriate repository;
provide license, version, DOI, full data dictionary, consent/privacy
screening and machine-reproducible build/validation scripts. Do not
archive vendor models, proprietary repos or third-party files without
rights. Note any publicly linked source URLs may disappear after the
snapshot and plan preservation by approved means.

## Independence and annotation roles (proposed, NOT performed)

- **R0, dataset steward:** validates frozen IDs, PR selection, version.
- **R1, provenance annotator A / R2, annotator B:** independently rate
  changed-line provenance; resolve disagreement only after both submit.
- **R3, rights reviewer:** checks file-level redistribution constraints.
- **R4, task curator:** reconstructs source-era specifications without
  reading held-out oracle results.
- **R5, independent oracle reviewer:** creates/tests sealed behavioral
  checks distinct from PR-added tests.
- **R6, isolation/security reviewer:** signs runner/no-network and
  independent five-meter evidence.
- **R7, contamination statistician:** adjudicates fork/issue/patch
  groups and leakage-safe splits; no label peek for model fitting.
- **R8, reproducibility auditor:** reruns extraction and validates
  all input/output SHA256 and disagreement protocol.

Templates/scripts exist for data quality; no fabricated R1--R8
assessments or approval records have been created. Only actual
qualified observations can support a Data Descriptor or ASE Results.

## Difference from AlphaCode

AlphaCode's public report concerns generation, clustering and
**external evaluation of solutions** in competitive programming
(primarily Python and C++), with a separate
[CodeContests data resource](https://deepmind.google/blog/competitive-programming-with-alphacode/).
U-CODE presently provides a much smaller metadata-derived
**repository-pull-request discovery** frame. The two targets,
denominators and evaluation oracles are not comparable.
The defensible next goal is demonstrably reproducible provenance,
rights-aware curation and independently testable repo repair tasks,
not a claim to have surpassed DeepMind's scale or performance.

## High-impact readiness conclusion

**Do not submit a Scientific Data Data Descriptor yet.** A quality-audited
120-row *PR metadata* sample can be openly shared as an intermediate
artifact, but the intended **multilingual executable task dataset**
still lacks the independent task/evaluator evidence that would make
it a meaningful task benchmark. The quality tooling and disclosed
negative results improve the methodological rigor of the ASE
manuscript right now. They do not manufacture the missing dataset.
