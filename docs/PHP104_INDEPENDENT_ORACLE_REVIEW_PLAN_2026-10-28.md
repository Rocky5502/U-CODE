# PHP #104 — independent evaluator design and source-rights review gate
*28 October 2026 · Public reviewer blueprint · No hidden tests included*

**Status: NOT AN EXECUTABLE TASK; NOT A SEALED ORACLE.**
This file is a reviewer-facing **design for an independent evaluation
package**, not that package. No result labels, expected paths, working
test scripts, sealed oracle hashes, reviewer endorsements, credentials or
patch implementation are included. The prospective case headings below
are public; a future independent evaluator must develop hidden cases and
expected outputs **privately**, without reusing the agent PR's added tests.

## Newly verified source chronology

The original [mvdbos/php-spider](https://github.com/mvdbos/php-spider)
repository's immutable pre-fix base commit
`25e9b1cf855669c24ba1609c7d4cfcda17ac6217`
was timestamped **22 October 2026, 22:07:39 UTC**. The publicly observed
parent [issue #166](https://github.com/mvdbos/php-spider/issues/166)
was created at **22:52:00 UTC** (2,661 seconds later), child
[issue #168](https://github.com/mvdbos/php-spider/issues/168)
at **22:53:10 UTC**, and PR
[#172](https://github.com/mvdbos/php-spider/pull/172)
at **22:55:42 UTC**. This is a strong temporal boundary for **source
code**; it is *not* a historical version archive of issue-body text.
Both currently viewed issue bodies were last updated after PR creation.

### Rights observations (not legal permission certification)

At that pinned base, root `LICENSE` blob
`9d2375c29942233e3b646d51210ebc67235df873`
contains a standard MIT notice naming Matthijs van den Bos (2023)
and requiring the copyright and permission notice be retained in
copies or substantial portions. `composer.json` declares `MIT`.
Read-only file observations at that same base found:

| Source | Observed notice | Limit |
| --- | --- | --- |
| `FilePersistenceHandler.php` | Author and copyright 2021 header | Authorship and derivative-file rights not independently adjudicated |
| `FileSerializedResourcePersistenceHandler.php` | Author and copyright 2021 header | Not a blanket permission for downstream dependency copies |
| `CachedResourceFilter.php` | Author docblock | No separate explicit per-file license header observed |
| `CachedResourceFilterTest.php` | Copyright header pointing to root `LICENSE` | Pre-PR test fixtures are not independently written gold oracles |

The [checked-in metadata-only blueprint](../data/admission/2026-10-28/php104_oracle_review_blueprint_PUBLIC_NO_GOLD.json)
pins each observed Git blob and encodes rights adjudication as
**false**. A qualified person still must review upstream dependencies,
authorship, redistributed artifacts, notice preservation and intended
use. The GitHub API and local code cannot authenticate that review.

## Independent oracle coverage requirements (PUBLIC DESIGN ONLY)

A reviewer who did **not** inspect PR #172's solution should
independently formalize permissible behaviors, expected outputs,
failure tolerances and selection of hidden cases from the pinned
pre-fix code and a genuinely ratified task statement.

| Family | Reviewer question | Main contamination threat |
| --- | --- | --- |
| `EMPTY_OR_ROOT_URI` | Are empty/root URI paths handled compatibly? | Reading the PR's generated fixtures |
| `TRAILING_SLASH_DIRECTORY` | Do directory-ending paths retain legacy behavior? | Treating the refactor helper as truth |
| `NESTED_URI_PATH` | Is multi-component URI layout preserved? | Deriving output from candidate's own helper |
| `ENCODED_BASENAME` | Are basename encoding and path identity consistent? | Encoding rules silently changed by the patch |
| `SPIDER_ID_NAMESPACE` | Does storage/cache identity remain isolated by spider ID? | Cache cross-contamination |
| `BASE_PATH_SEPARATOR` | Are base-directory separator conventions preserved? | OS/runtime path dependence |
| `REAL_WRITER_CACHE_LOOKUP` | Can real persistence be retrieved by cache lookup? | Both sides agreeing on the same incorrect algorithm |
| `CACHE_FRESHNESS_BOUNDARIES` | Are age/missing/expired cases handled as before? | Wall-clock drift and nondeterminism |
| `PROTECTED_NAMING_EXTENSION` | Are supported extension hooks still exercised? | Assuming arbitrary subclass compatibility |
| `INDEPENDENT_LEGACY_FIXTURE` | Does a legacy cache resource remain retrievable? | Copying PR-authored expected fixtures |

This matrix is a **coverage checklist**, not completed coverage.
It explicitly requires cross-component writer/reader assessment
and an independently derived legacy fixture because a passing test
that recomputes expectations from the same shared implementation
may be circular. For every family, an external reviewer must decide
the actual independent assertion, fixture, exception behavior and
platform constraints. Do not post evaluator-only logic in public
branches, PR discussions or agent prompts.

## Two scientifically distinct paths — choose deliberately

**Path A — historically faithful PR-replay task.**
Obtain a verifiable original issue-body snapshot or contemporaneous
task artifact available *before* PR #172 creation. Two independent
reviewers must check its authenticity and reproducibility without
consulting the solution. If this cannot be established, **do not**
call this a validated historical AI-agent PR repair task.

**Path B — newly specified, prospective repair task.**
Independent reviewers may instead write a new, explicit behavior
contract grounded in the pinned base source, with documented creation
time, ownership, acceptance domains and permissible alternatives.
This creates a **new prospective task**, not a reconstruction of the
original developer's exact intent or a validated historical agent PR.
Record Path B in a separate dataset stratum and report denominators
separately. Do not reuse prior PR outcome or bot-authorship claims as
the new task's ground truth. This is a defensible possible fallback
when genuine pre-PR issue-text snapshots do not exist.

Neither path is authorized today. A real evaluator also requires
source permissions, independently written sealed tests, a verified
toolchain and a rootless network-disabled disposable runner with
independently trusted five-dimensional metering.

## Exact external-review completion criteria

A future approved evaluator must document, **outside the public
U-CODE tree**: the signed/independently verifiable source-spec era
and chosen Path A/B; rights clearance with notices; evaluated
repository base and source SHA; oracle authorship independence;
sealed test suite version/commitment; pre-registration before agent
access; trusted sandbox boundaries; PHP toolchain/locked dependencies;
an independent token/test/GPU/CPU/wall accounting mechanism; and
the policy-to-evaluator isolation/audit log. A code-generated signature,
unchecked reviewer name, or locally typed SHA is insufficient.

A *public* gate status may describe that external review has
**not** yet occurred; it must never contain secret expected
outputs or a self-asserted experimental approval. If any gate fails,
report task exclusion and preserve the denominator, not optimistic
success percentages.

## Reproduction without third-party execution

```bash
python -m scripts.verify_php104_source_contracts
python -m scripts.verify_php104_oracle_blueprint
python -m unittest discover -s tests -v
```

These commands verify static reference identities, pre-fix timing,
the ten proposed case families, observed copyright notice categories,
the absence of public gold outputs, and fail-closed approval flags.
They neither compile PHP nor establish any independent oracle or task
success. The first-party Python code has *no evaluator call site*.
