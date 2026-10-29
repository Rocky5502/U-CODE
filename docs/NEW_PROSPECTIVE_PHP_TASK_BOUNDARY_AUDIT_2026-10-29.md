# PHP #104 — prospective task contract and policy-input integrity (29 October 2026)

**Status:** NEW UNAPPROVED RESEARCH PROPOSAL. **Not** an original historical
issue snapshot; **not** a benchmark admission, runner authorization, hidden
evaluator, or real coding-agent experiment.

## Why the task needed a new namespace

[PHP source lead #104](https://github.com/mvdbos/php-spider/pull/172)
is the October 22, 2026 pull request for `mvdbos/php-spider`. The pinned
original base is `25e9b1cf855669c24ba1609c7d4cfcda17ac6217`;
[the original source-evidence packet](PHP104_BASE_SOURCE_CONTRACT_REVIEW_2026-10-28.md)
provides read-only file observations at that commit.

Parent issue #166 was created 2026-10-22T22:52:00Z, child issue #168
2026-10-22T22:53:10Z, and PR #172 2026-10-22T22:55:42Z. The current
issue body is not an authenticated body-as-of-PR-creation snapshot.
GitHub issue updated timestamps do not, by themselves, authenticate
edits or reconstruct earlier versions. The existing historical PR task
therefore remains NOT ADMITTED.

To make real experimental progress without rewriting history, a **separate
new prospective review proposal** now lives at:

- `data/admission/2026-10-29/php104_NEW_PROSPECTIVE_DRAFT_REVIEW_ONLY.json`
- `src/ucode/prospective_task_contract.py`
- `scripts/validate_php104_prospective_draft.py`
- `tests/test_prospective_task_contract.py`

The `task_namespace` is
`prospective:source-lead:104`. Its earliest claimed creation date is
**2026-10-29**, later than the October 22 pull request. It MUST be
reported in a prospective task cohort, never pooled as a historical
agent-authored PR replay or pre-PR contemporary issue snapshot.

## What the draft specifies

It proposes a *future externally reviewable* PHP repository-repair
contract concerning the legacy file writer and cache lookup path
semantics, URI path completion, encoded basenames, spider-ID
isolation, freshness, writer/reader interoperability and supported
extension hooks. These are possible invariants suggested by read-only
pinned base-source observations — **not independent normative
requirements, gold output fixtures, solution patches, or discovered
behavioral truths**. Independent reviewers must ratify or revise the
requirements without consulting the PR solution, and must determine
the actual full-task correctness oracle separately.

The draft cross-checks all five reported source-observation identities
against the existing frozen read-only PHP source-leads JSON and rejects
any substitution with the post-fix `FilePersistenceLayout.php`
path, wrong Git SHA, missing lead or changed source identity.
A SHA256 fingerprint of this *public draft* detects later changes, but
it is **not cryptographic proof of its creation date, provenance,
third-party approval or oracle independence**.

## Hard fail-closed guardrails

The schema enforces nine negative facts: historical original issue body
not attested; independent new spec review not completed; file rights
not cleared; hidden oracle not sealed; toolchain unverified; runner
unattested; five physical meters unauthenticated; external code not
executed; experimental eligibility false.

It rejects unknown fields such as `gold_patch`, extra oracle-test
payloads, `head_sha`, `post_fix_solution` and forged approval fields.
No method promotes it to `AgentTaskView` or executes anything. Its
only output is a **reviewer-only** metadata summary, not policy-visible
task instructions. Future task admission must be a separate and
independently supervised evidence-backed protocol.

### Additional source-integrity repair

`EvaluatorRegistration.issue_ref` previously required only the prefix
`https://github.com/`, not an exact repository-linked issue URL.
A wrong-repository issue or query/fragment could masquerade as the
registered task's reference. It now requires
`https://github.com/<original owner>/<original repo>/issues/<positive number>`
with no suffix, credentials, query or fragment. The repository
identity is also validated explicitly.

`AgentTaskView.prefixed_spec` now rejects C0/C1 control bytes,
bidirectional/zero-width format overrides, and unpaired surrogate
characters; ordinary Unicode, including Mandarin and Nepali, plus
newlines and tabs remain valid. This only prevents text-shape
ambiguity: it **does not** prove an issue text authentic or remove
natural-language prompt injection.

## Reviewer work needed before real trials

1. Choose **prospective** scope explicitly and approve the exact new
   task statement with independent reviewer identities and dated,
   externally verifiable records; do not pretend to recover the
   historical issue.
2. Review source-file license and derivative use rights with accurate
   notices, and independently adjudicate candidate code authorship.
3. Independently derive and seal the private repository-level
   functional evaluator with expected outputs, negative cases,
   acceptable alternate implementations and non-leakage safeguards;
   PR-authored tests cannot serve as its independent oracle.
4. Pin PHP, Composer dependencies and source blobs, reproduce the
   base state with known-good clean-room restoration, and validate a
   disposable rootless, network-denied isolated runtime on an
   authorized host.
5. Obtain verifiable token, test, GPU, CPU and wall time hard
   measurements for the eventual matched treatment and baseline.
6. Pre-register model, policy, seed, budget and task assignment
   matrices without peeking at evaluator-only results; preserve
   infrastructure failures in intent-to-treat denominators.

**Current admitted real repository tasks: zero. Current real matched
LLM repair results: zero.** This work advances reproducible source
identity and reviewer coordination, not empirical claims.

## Offline reproduction

```bash
python -m scripts.validate_php104_prospective_draft
python -m scripts.check_evaluator_boundary
python -m unittest discover -s tests -v
```

The draft validator is an explicit CI step. It does not pull a PHP
repository, install Composer, run PHP, authorize Docker, contact
external reviewers, or generate an independent hidden oracle.
