# Data governance, provenance and repository safety

**Discovery is not authorship.** The 120-entry file contains GitHub search matches,
10 each for 12 GitHub primary-language categories. All records begin with
status UNVERIFIED_CANDIDATE and MUST remain so until further evidence is obtained.

## Sequential evidence states

1. Discovery match: URL, PR number, query language.
2. Metadata-supported: GitHub API confirms expected bot account, merger, source
   changed-file paths and immutable base/head identifiers.
3. Authorship-reviewed: independent reviewer attributes patch/file ownership to
   actual agent and checks mixed human edits.
4. Rights-cleared: source and file-level licenses checked; no secrets or PII.
5. Reproducible: build/test succeed in a pinned isolated container.
6. Outcome-labeled: evaluated on independent test oracles; merge is NOT a correctness oracle.

The provided audit command performs stage 2 triage only. It cannot infer complete
AI authorship, detect all licenses, or assess code behavior. Missing evidence is
recorded as UNKNOWN or NOT CHECKED. Rate limits yield retrieval_failed records.

## Vetted sample schema (future)

sample_id, cohort, repository, agent_pr_url, agent_name, base_sha, head_sha,
merge_commit_sha, PR datetime, patch_files, source_extensions, attributable_lines,
license_review, redistribution_allowed, source_bytes, test_container_digest,
independent_tests, verifier_outcome, verifier_limitations, annotator_ids.

Do not publish 2–5 GB of third-party code until permission is established.
Size target refers to selected patch/source/test artifacts, not model weights,
Git history, artifacts or dependencies. This repo's MIT license covers only
its original U-CODE implementation, not the linked sources or model weights.

## Privacy and execution

Do not download and execute random PRs automatically. Vetted code must run
in disposable, network-disabled, nonprivileged containers with resource and
wall-clock caps and no host credentials or mounts. No such execution facility
is enabled in this repository. Repository API auditing is READ ONLY.

Keep GitHub tokens in GITHUB_TOKEN environment variable; never commit tokens,
original user transcripts, API keys, personal records or hidden test oracles.
Respect gated SWE-chat terms and model license restrictions.

## Evaluation contamination

Split by related repository and fork family, commit chronology and duplicate
patch clustering. Do not condition verifier policy on gold patch or post-test
labels. Publish sample attrition tables and negative/failed-run statistics.
