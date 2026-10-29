# U-CODE source-era task feasibility and Springer novelty audit — 29 October 2026

**Decision:** source-only research sprint, **not** real-task admission, real
LLM inference, independent review, a hidden functional oracle or a submitted
journal paper. No experiment outcome, risk reduction, cost saving or cross-language
generalization can be concluded.

## A. What the publisher actually requires

Official special issue:
https://link.springer.com/collections/jjcfecffai

- *Automated Software Engineering* collection **Search-Based Software
  Engineering in the Era of LLMs and Agentic Systems** remains open with a
  **30 January 2027** submission deadline.
- SBSE for AI-generated code, hybrid LLM/search, agent control and reproducible
  empirical assessment are listed as relevant topics.
- The journal requires LaTeX with `sn-jnl`, a **150–250 word abstract**,
  **4–6 keywords**, and a complete statements/declarations section. The
  reviewed paper must be original and not simultaneously under review elsewhere.
  See https://link.springer.com/journal/10515/submission-guidelines.
- The source of the paper is in GitHub. The finished, compiled PDF and
  authenticated Overleaf collaboration remain unverified.

## B. Fresh read-only original-issue review

Sources inspected on 29 October 2026 (GitHub REST public issue and timeline
endpoints; current content is mutable and this is not an independent archive):

| Lead | Pinned issue | PR starts | Issue-created lead | Current issue description | Assessment |
|---|---|---|---:|---|---|
| PHP #104 | [mvdbos/php-spider issue #168](https://github.com/mvdbos/php-spider/issues/168), with [parent #166](https://github.com/mvdbos/php-spider/issues/166) | [#172](https://github.com/mvdbos/php-spider/pull/172) | 152 s | Specific compatibility and shared-layout requirements, with parent issue detail | Best next independent reviewer target; **NOT admitted** |
| Go #43 | [PlayHuai/eighty-point-huai-an issue #29](https://github.com/PlayHuai/eighty-point-huai-an/issues/29) | [#30](https://github.com/PlayHuai/eighty-point-huai-an/pull/30) | 8 s | Short T10/T09/T07 task tracker, without stable settlement correctness rules | Hold; **NOT admitted** |

The PHP parent issue was created at 2026-10-22T22:52:00Z and the child at
22:53:10Z; PR #172 began at 22:55:42Z. The child was last updated at
23:03:40Z, after PR creation; this can be caused by closing the issue,
and **does not establish that the body was edited**. The Go issue was created
at 2026-10-23T12:18:50Z; PR #30 started at 12:18:58Z, eight seconds later.
Go issue `updated_at` was 13:07:52Z after PR creation. Public GitHub
timelines show events, not a complete cryptographically authenticated
historical version of the issue body.

A present-day issue body is therefore **quarantined from the policy input**.
Its detailed or brief contents are a reviewer lead only. The metadata file
`data/admission/2026-10-29/live_issue_current_body_review_metadata.json`
records current issue observations, not descriptions, patches, hidden tests,
expected outputs or authorizations. It uses a post-review UTC recording
timestamp only; that timestamp is NOT the issue's original publication time.
The new `audit_live_issue_observations` validator strictly checks source
identity against the frozen two-case chronology and rejects promotions,
unknown fields and time inconsistencies. It can never admit a task.

## C. What would actually unblock PHP #104

**Historically faithful PR-replay cohort:**
1. Obtain independently verifiable issue/spec content demonstrably available
   **before** PR #172 and check whether its requirements were already stable.
   Current issue text and missing `edited` events are insufficient.
2. Independently adjudicate code and dependency use rights with exact notices
   and file scope. A root MIT declaration is not a third-party rights audit.
3. Blindly specify behavioral expectations, fixtures and exception cases from
   legitimate task-era requirements and pre-fix behavior, without inspecting
   PR #172's patch or PR-authored tests. Keep evaluator-only cases private.
4. Validate a version-pinned nonprivileged, no-network, disposable runtime
   and independently measured token/test/GPU/CPU/wall caps.
5. Require separate human independent signoff and a sealed evaluator before
   any task receives an execution-ready admission decision.

**Prospective specification reconstruction cohort:** if historical issue
text cannot be recovered, an independent reviewer may prospectively author a
new specification using legitimate pre-fix public evidence. Label the task
as *prospectively reconstructed*, never as a faithful reproduction of what
the agent historically received. Keep historical and reconstructed strata
separate in RQ1, RQ3 and RQ5; predeclare exclusions and denominator changes.

For Go #43, independently recover pre-PR T10 acceptance criteria, scoring
semantics, remainder tie-break rules, transaction/idempotency guarantees and
permitted settlement outputs before investing in a hidden evaluator. The
later PR body is NOT original task wording.

## D. More demanding novelty boundary

- [SWE-Search (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a1e6783e4d739196cad3336f12d402bf-Abstract-Conference.html)
  already uses tree search and iterative coding-agent refinement.
- [Guided Search Strategies (ICML 2025)](https://proceedings.mlr.press/v267/zainullina25a.html)
  already offers action-value-guided lookahead and trajectory selection
  in non-serializable software-agent environments.
- [SearchSYS (Automated Software Engineering, 2025)](https://doi.org/10.1007/s10515-025-00531-7)
  already uses LLM-derived inputs plus search-based fuzzing and reports
  executable simulator bugs.
- Existing U-CODE citations include PATSSEL, SWE-Verifier, SWE-Replay,
  RETRACE and Dockerless; do not misrepresent these methods as
  uncertainty-free or as lacking all verification.

**Falsifiable differentiation:** the marginal value of
*history-conditioned, potentially redundant diagnostic evidence*
against *generating/repairing a new candidate* under five distinct hard
resource caps, matched proposals and an evaluator-only correctness oracle.
This is a **hypothesis**, not established superiority, and strong MCTS,
value-guided search and verifier comparators are compulsory.

## E. Verification and next actual study

Run:

```sh
python -m unittest tests.test_live_issue_spec_quarantine -v
python -m scripts.audit_live_issue_spec_quarantine
python -m scripts.audit_overleaf_sources
python -m unittest discover -s tests -v
```

The tests validate *first-party source metadata only*. Even passing full CI
does not demonstrate source-era body authenticity, rights, trusted container
metering, a sealed evaluator or any software-repair success.

**Next critical external action:** obtain a real independent source-era
specification and evaluator reviewer for PHP #104, or exclude it and select
a better original task from the queued candidates. Do **not** buy a GPU or
claim real results while those conditions remain unfulfilled.
