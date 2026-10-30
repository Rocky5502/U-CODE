# Source-era task milestone: Go #43 immutable specification-file crosswalk

**30 October 2026 — metadata verification only; zero external tasks admitted.**

## Why this new check matters

The evaluator registration for the historical Go source lead
[PlayHuai/eighty-point-huai-an PR #30](https://github.com/PlayHuai/eighty-point-huai-an/pull/30)
declares a `pre_fix_spec_blob_sha`. Previously, the registration verifier
checked only that the field looked like a 40-digit Git object identity.
It did not ensure that the declared SHA belonged to the *specific
policy-visible document path* in the fixed pre-fix repository tree.
An apparently immutable but incorrect or post-fix document could
therefore pass that **weak identity check**. The registration was
still always research-ineligible; this fixes a provenance gap, not a
bypass that had authorized real execution.

## Official read-only GitHub tree observation

The following public Git metadata was observed on 2026-10-30, without
cloning or executing third-party source:

| Field | Pinned observation |
|---|---|
| Candidate and repository | #43 / `PlayHuai/eighty-point-huai-an` |
| Historical PR | `https://github.com/PlayHuai/eighty-point-huai-an/pull/30` |
| Pre-fix base commit | `ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a` |
| Git base tree | `e53fb011857926632c4a4ec8752425e0f2b41559` |
| Pre-fix document path | `docs/design.md` |
| Git document blob | `b566ca7627b6518670a866a6a637bd5257e947f4` |
| Tree-entry file mode / type | `100644` / `blob` |
| Tree-entry size | **16,052 bytes** |
| Tree API response | `git/trees/<tree-sha>?recursive=1` (nontruncated in previously frozen tree metadata) |

[Original immutable file link](https://github.com/PlayHuai/eighty-point-huai-an/blob/ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a/docs/design.md) |
[Git tree endpoint](https://api.github.com/repos/PlayHuai/eighty-point-huai-an/git/trees/e53fb011857926632c4a4ec8752425e0f2b41559?recursive=1).

The fixed Git tree's `docs/design.md` entry was compared against
the identity in `prospective_oracle_registrations.jsonl`.
The new offline manifest `data/admission/2026-10-30/go43_immutable_pre_fix_spec_blob_METADATA_NOT_APPROVED.json`
records those observations as **untrusted, reviewable metadata**, not
as a signed provider receipt. Independent reproducibility requires
separately re-fetching the referenced Git objects and checking their
identities against Git object hashing; the local manifest alone cannot
cryptographically attest their provenance.

## What was changed in source code

- `src/ucode/pre_fix_spec_binding.py` compares exact candidate ID,
  repository, pre-fix base SHA, tree SHA, document path, blob object SHA,
  object type, Git mode, size, and frozen policy-visible GitHub URL.
- The new routine also ties the base commit and tree identity to the
  **previously frozen two-candidate base-tree inventory**, and refuses
  any fabricated oracle approvals, rights clearance, task eligibility,
  executable source claim or alleged pre-PR issue-body snapshot.
- `scripts/check_evaluator_boundary.py` now **requires the source
  crosswalk on every standard evaluator-registration audit**.
- Historical PHP candidate #104 is separately locked to its **mutable
  issue URL without a fake pre-fix spec blob**, and cannot be promoted
  through the Go document-binding path. Its newer prospective task
  draft is a distinct namespace and still requires external approval.
- `tests/test_pre_fix_spec_binding.py` includes adversarial checks for
  substituted document SHAs, different same-commit paths, changed
  tree/commit identity, forged rights/oracle approval fields,
  duplicate candidate IDs, retroactive observation dates and
  modified input registrations.

## Scientific limitation: source authenticity is not task adequacy

**What the checker now establishes, subject to provider metadata
authenticity:** a correctly pinned *document object identity* at the
Go candidate's pre-fix repository snapshot.

**What it cannot establish:** that the complete design document is
the unambiguous intended specification of PR #30; that its current
contents are properly applicable to the independently adjudicated
task scope; independent acceptance of ambiguous settlement edge
cases; document revision chronology beyond the pinned base;
file-level source rights; AI authorship; runnable Go toolchain;
independent sealed functional evaluator; container isolation;
authenticated physical five-resource metering; or policy calibration.

In particular, the historical Go issue and the original document
include settlement language that leaves possible valid alternative
tie-breaking decisions. A gold test should **not** adopt the PR
author's chosen tie-break just because it appears in a post-fix patch.
A separately authorized business-rule reviewer must adjudicate
acceptable outcomes, and distinguish a reduced scoring microtask
from a complete repository/transaction correctness benchmark.

### Reproduce (first-party only)

```bash
python -m scripts.check_evaluator_boundary
python -m unittest discover -s tests -p 'test_pre_fix_spec_binding.py' -v
python -m unittest discover -s tests -v
```

None of these commands executes Go, PHP, the candidate repository, a
new hidden oracle or an LLM. The script outputs
`independently_admitted: false` for both historical candidates.

## Next legitimate real-task gates

1. Obtain **independent behavioral-spec adjudication** of the Go scoring,
   settlement and rank requirements including permissible remainder
   distribution, or independently ratify the *new* prospective PHP task.
2. Perform specific-file reuse rights and author-lineage review.
3. Have a genuinely separate evaluator author and seal correctness tests
   outside all policy and retrieval inputs; authenticate access
   boundaries and revision receipts.
4. Reproduce a fully isolated, network-denied, rootless runner on an
   authorized host and independently enforce/meter all five resource
   dimensions, including controller CPU/wall costs.
5. Freeze model checkpoint hashes, seeds, matched opportunities and
   full-task versus microtask estimands before any code-generation trial.

**Current empirical status:** 0 independently admitted external executable
tasks, 0 sealed independent oracles, 0 real matched six-model results,
0 admissible empirical success estimates. The only new evidence is a
reproducible source-object crosswalk and stricter fail-closed controls.
