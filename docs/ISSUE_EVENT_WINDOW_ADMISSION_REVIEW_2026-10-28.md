# Source-era GitHub issue-event feasibility audit — 28 October 2026

**Evidence class:** public GitHub issue Events REST API, read only, first page
(`per_page=100`) of two original issue numbers, checked against the
pinned pre-fix task chronology and GitHub PR SHA dossier. **Not source
execution, not historical issue-body capture, not independent oracle
approval, not a qualifying runnable task.**

## Exact source and observations

| Candidate | Original issue (first-page events) | Issue-to-PR time | Observed before PR | At/after PR | Implication |
| --- | --- | ---: | ---: | ---: | --- |
| #104 PHP | [mvdbos/php-spider #168](https://github.com/mvdbos/php-spider/issues/168), [GitHub events API](https://api.github.com/repos/mvdbos/php-spider/issues/168/events?per_page=100) | 152 seconds | one `labeled`, two `assigned` | one `connected`, one `closed` | Plausible genuine pre-PR work assignment; **no issue-text history** |
| #43 Go | [PlayHuai/eighty-point-huai-an #29](https://github.com/PlayHuai/eighty-point-huai-an/issues/29), [GitHub events API](https://api.github.com/repos/PlayHuai/eighty-point-huai-an/issues/29/events?per_page=100) | 8 seconds | two `assigned` | one `connected`, one `closed` | Extremely short prior window; **no issue-text history** |

Observed event IDs, types and UTC timestamps only are stored in
[`two_candidate_issue_event_first_pages.json`](../data/admission/2026-10-28/two_candidate_issue_event_first_pages.json).
The metadata contains no issue body, patch diff, hidden tests, secret or
oracle outcome. It is a static record of the first requested API page;
headers, pagination and historical completeness are **not authenticated**.
The GitHub issue Events API does not provide an immutable full version
archive of body text. The *absence* of an `edited` entry is NOT evidence
that content never changed. Likewise, current `updated_at` after PR
creation can reflect a close event rather than a text edit.

## Explicit scientific decision

**Neither PHP nor Go is admitted.** These records justify investigation,
not pre-fix-spec provenance. A partial pre-PR issue/PR event timeline
cannot establish exactly what a developer or agent knew at task creation.
Our manual screen of current issue descriptions found PHP more detailed
than Go, but both are post-observation states. They cannot be copied to a
policy prompt as validated pre-fix requirements.

The Go base tree contains an earlier `docs/design.md` blob, yet the
settlement remainder tie-break remains ambiguous; an evaluator must
independently define permitted outcomes and transaction/idempotency
requirements before sealing tests. Do not use post-fix patch behavior as
gold specification. PHP also needs source-era requirements, file-level
rights and an independently authored evaluator oracle.

## Implementation and threat checks

`src/ucode/issue_event_window_audit.py` verifies schema allowlists,
canonical candidate identity, immutable dossier-linked issue/PR metadata,
strict typed event IDs, sorted valid UTC timestamps, first-page size,
event date bounded by observation day, no repetition and no self-approval
flags. `scripts/verify_issue_event_windows.py` prints a deterministic
source-free report. CI runs it independently under Python 3.10 and 3.12
alongside adversarial `tests/test_issue_event_window_audit.py`.

**Threats:** GitHub API event semantics can omit body changes, edited
event history may be absent, API responses are not cryptographically
attested by this repository, upstream source rights remain unreviewed,
and event IDs may exist on different pagination pages not yet checked.
No exact full-history claim, source reuse approval, synthetic human
review or completion of any of the eight admission gates is made.

**Next external gate:** obtain independently verifiable *as-of-PR*
specification text (time-stamped archival or independently approved
source-era commit and requirements), independent rights and oracle
adjudication, and a rootless network-disabled trusted evaluator runner.
If these cannot be obtained, reject candidates rather than treating
current issue bodies or PR-authored tests as evidence.
