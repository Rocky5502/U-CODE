# PHP candidate #104 — independently reviewable source-era contract leads

**Audit date:** 28 October 2026. **Classification:** first-party, read-only,
source-informed reviewer packet. **Do not feed this file or its current-issue
text to an evaluation agent.**

## Narrow original task

The PHP candidate is
[mvdbos/php-spider PR #172](https://github.com/mvdbos/php-spider/pull/172)
at pinned base commit
`25e9b1cf855669c24ba1609c7d4cfcda17ac6217`,
base tree `6924b6560484f3c28fcbb7359a15df2540c55d22`.
The current issues form this chronology:

- [Parent issue #166](https://github.com/mvdbos/php-spider/issues/166):
  created **2026-10-22 22:52:00 UTC**, observed last updated
  **2026-10-23 09:03:25 UTC**.
- [Child issue #168](https://github.com/mvdbos/php-spider/issues/168):
  created **22:53:10 UTC**, observed last updated **23:03:40 UTC**.
- PR #172 created **22:55:42 UTC** on the same day.
- Parent predates child by **70 seconds** and PR by **222 seconds**;
  child predates PR by **152 seconds**.

The *currently visible* parent issue articulates compatibility and
shared-layout requirements, but its text is **not proven to be the exact
pre-PR body**. The public GitHub issue Events API does not provide a
trustworthy, immutable version history for issue descriptions. Neither an
earlier issue creation timestamp nor the absence of an edit event
resolves this missing evidence.

## What was seen in immutable base-source Git blobs

The observations below refer exclusively to **original pre-fix**
Git blobs, fetched read-only from the official repository at that exact
base commit on 28 October. No source is vendored or redistributed.

| Reviewer-only lead | Base source file | Pinned Git blob | What the unexecuted source suggests |
| --- | --- | --- | --- |
| Path completion | `src/PersistenceHandler/FilePersistenceHandler.php` | `1edebb7…` | Empty/root or trailing slash path handling appends the default filename |
| Basename encoding | Same file | `1edebb7…` | URI path basename is URL encoded as stored filename |
| Serialized writer | `src/PersistenceHandler/FileSerializedResourcePersistenceHandler.php` | `96d3e27…` | Resource serialization and filesystem writes compose with the base layout hooks |
| Cache lookup / freshness | `src/Filter/Prefetch/CachedResourceFilter.php` | `7674093…` | The pre-PR cache lookup builds its own compatible filename path and applies an independent freshness rule |
| Original fixture duplication | `tests/Filter/Prefetch/CachedResourceFilterTest.php` | `e6c9e6e…` | Existing pre-fix test helper repeats the cache layout algorithm; agreement in such fixtures is not independent path compatibility evidence |

The exact full blob SHA values and bounded concept IDs are in
[`php104_base_source_contract_leads.json`](../data/admission/2026-10-28/php104_base_source_contract_leads.json).
The read-only tree index previously established the pinned core
`FilePersistenceHandler.php` and `CachedResourceFilter.php` SHA IDs,
whereas the two additional blob identities above were separately observed
read-only at the same base commit. This is **static interpretation, not
runtime validation**. A source observation can be incomplete or mistaken
and should not be treated as an oracle assertion.

## Independently testable requirements: only prospective possibilities

An independent, genuine evaluator should decide (without consulting the
PR solution or PR-authored tests) whether to test: legacy URI-to-filename
compatibility; writer-to-reader roundtrip through a disposable scratch
directory; isolation by spider ID; cache age semantics; and supported
protected-extension naming hooks. Do not derive expected filenames from
the patched shared helper itself. A complete repo-level task should also
preserve freshness, serialization and existing test behavior; validating
only a path function would be an explicitly narrower microtask, **not**
full PR correctness.

## Hard blockers and research integrity

1. Parent and child issue *original body text as of PR creation* is not
   independently archived. The latest issue wording **may** have changed.
2. The developer's original requirements are not independently ratified
   into a frozen policy-safe task statement. Source behavior is evidence
   to review, not a trusted target.
3. Full file-level license/attribution and LLM-versus-human line ownership
   are not adjudicated. Root MIT metadata does not approve every use.
4. An independent hidden functional oracle has not been authored, reviewed
   or sealed, and no real evaluator has executed.
5. Dependency versions, PHP runtime, network-disabled rootless sandbox and
   audited token/test/GPU/CPU/wall metering have not been established.

The `php104_source_contract_audit.py` verifier checks immutable
reference identities, dates and absence of forged approval fields; it
cannot authenticate GitHub independently or prove the contents of
these Git objects. Adversarial unit tests are source-free, non-executable
metadata tests. **Task admission remains zero**. No evidence herein
justifies six-model GPU trials, submitted journal Results, or live
Overleaf synchronization.
