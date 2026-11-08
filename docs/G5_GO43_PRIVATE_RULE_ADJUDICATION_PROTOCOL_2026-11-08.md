# Go #43: private paired domain-decision review — no oracle or admission

**8 November 2026 · public methods note · not a claim of actual independent review**

This source-controlled module is a handoff tool for a **future real human specification review**. It does not contain any completed reviews or judgments about how the game actually settles. The two immutable original Go #43 documents are the basis of the [specification feasibility packet](G5_GO43_SPEC_FEASIBILITY_DECISION_PACKET_2026-11-08.md). The project still has **six unresolved Go normative questions, twelve prospective reviewer case families, eight pending Go admission gates and eight pending PHP gates**.

## Why this separate six-question review is needed

Existing [12 × 8 generic admission review forms](G5_PRIVATE_REVIEW_TRIAGE_2026-11-07.md) assess whether candidate provenance, rights, oracle, secrecy, sandbox, toolchain and resource receipts are present. They **do not** distinguish two independent *domain interpretations* of the Go rules in §3.2 and §7. Before an authorized evaluator creates any gold test, a competent domain owner must decide if the pre-fix task can be specified at all.

This additional review uses the exact **same six question IDs** from the source-pinned public blueprint:

| Source-era question | Independent adjudication required |
|---|---|
| `ZERO_FLOOR_VS_TOTAL_CONSERVATION` | Specify the correct behavior when losers cannot pay the nominal loss, rather than copying a PR patch |
| `HALL_COEFFICIENT_FRACTIONAL_ROUNDING` | Determine fixed wallet units, fractional persistence or rounding, backed by pre-fix rules |
| `TEAM_PLAYER_SPLIT_AND_NONNEGATIVE_BALANCE` | Specify per-player/team distribution and account boundaries |
| `SPRING_RULE_SOURCE_AND_SCOPE` | Confirm which pre-fix two-match spring conditions actually apply |
| `ATOMIC_RETRY_IDENTITY_AND_OBSERVABILITY` | Specify atomic writes, retry keys, observable recovery and partial failures |
| `EXTERNAL_BUSINESS_RULES_PRECEDENCE` | Decide whether `docs/design.md` and higher-priority `docs/淮安80分业务规则.md` normatively cover the **microtask**, not the entire PR |

**No human signoff was performed.** Neither a file SHA nor agreement on a memo hash proves which interpretation is correct or creates a hidden oracle.

## A/B private reviewer workflow (only when human reviewers exist)

Have two qualified domain reviewers independently inspect original historical documents and submit **separate private decision memos**, without using post-PR patches, PR-authored tests or evaluator outcomes. An independent adjudicator should reconcile disagreements **outside ChatGPT, public GitHub, GitHub Actions or the coding policy**. The only public information in this repository is the question ID, source anchor and an abstract triage procedure.

Generate two **blank** private JSONL forms locally into a newly created directory **outside** the repository:

```bash
python -m scripts.triage_go43_domain_decisions \
  --export-blank-dir /private/ucode-go43-domain-review
```

This writes `A_go43_PENDING.jsonl` and `B_go43_PENDING.jsonl` with restrictive permissions on POSIX. Share the forms separately with independent reviewers; do not publish the completed versions. For actual returned human reviews, the reviewer-controlled local machine can compare their private files and produce only a redacted status summary:

```bash
python -m scripts.triage_go43_domain_decisions \
  --reviewer-a /private/A_go43_completed.jsonl \
  --reviewer-b /private/B_go43_completed.jsonl \
  --output /private/go43_redacted_status.json
```

Without inputs, this prints the six questions as **PENDING**, which is the only legitimate CI mode:

```bash
python -m scripts.triage_go43_domain_decisions
python -m scripts.triage_go43_domain_decisions --require-adjudicated
# The second command deliberately exits 2; this code cannot authorize a task.
```

The parser requires exactly six immutable source-bound rows per reviewer; rejects extra privileged fields, NaN, duplicated JSON fields, duplicate/missing questions, false approvals, oversized files and symlinked inputs; and refuses completed reviewer inputs stored inside the Git checkout. It redacts reviewer names, free-text rationales, source URIs and memo digests. Each private positive claim must include a digest of the original reviewer memo, source references and a rationale, yet these claims are still **untrusted**.

## How the disagreement categories should be interpreted

| Private pair | Redacted status | Action |
|---|---|---|
| Either reviewer pending | `PENDING_INDEPENDENT_DOMAIN_REVIEW` | Get missing review, do not infer a rule |
| Different verdicts | `DIVERGENT_VERDICT_NEEDS_INDEPENDENT_ADJUDICATION` | Independent human investigates |
| Both report memos, different digests | `DIVERGENT_MEMO_DIGEST_NEEDS_INDEPENDENT_ADJUDICATION` | Distinct memo bytes may express the same semantics; adjudicate content independently |
| Equal claimed memo digest, different source refs | `DIVERGENT_SOURCE_REFS_NEEDS_INDEPENDENT_ADJUDICATION` | Reconcile pre-fix authority and citations |
| Same claimed memo digest and refs | `MATCHING_UNVERIFIED_RULE_MEMO_CLAIMS_NOT_ADJUDICATED` | Structural agreement only; no verified human independence, meaning or oracle |
| Both reject task scope | `BOTH_REJECT_SCOPE_NO_TASK_ADMISSION` | Exclude or independently re-scope the task |
| Both lack adequate source evidence | `BOTH_INSUFFICIENT_SOURCE_EVIDENCE_NO_TASK_ADMISSION` | Seek authentic pre-fix context or exclude |

This workflow **does not assert that the same SHA256 proves independent authorship or correct normative semantics**. Two reviews can quote different textual explanations and still agree semantically. A qualified adjudicator must review actual private content and resolve the behavior in a separately approved, pre-outcome task specification. Domain review is necessary but **not sufficient** for file-level reuse rights, trusted private oracle construction, safe execution, model or budget approval.

## Engineering and scientific limits

- Code: [private decision-schema triage](../src/ucode/go43_domain_decision_triage.py) and [local-only CLI](../scripts/triage_go43_domain_decisions.py).
- Tests: [synthetic/adversarial reviewer tests](../tests/test_go43_domain_decision_triage.py); **fabricated reviewer names, notes and hashes exist in tests ONLY**, never represented as human study data.
- CI: validates the six **blank** statuses and strict blocked exit code without generating or reading private reviewer files. No third-party code executes.
- R0–R16 virtual roles are not actual independent people; a reader must never convert this internal review script or its testing into external expertise or human-subject data.
- Source hashes are not proof of rights or correct rules. `Go #43 = 8/8 PENDING`, `PHP #104 = 8/8 PENDING`. Independently approved tasks: **zero**. Sealed functional oracles: **zero**. Real policy outcomes: **zero**.
- The registered six-model/eight-policy/five-resource prospective comparison is untouched; the Springer GitHub LaTeX source is not the live Overleaf editor.

**Next scientific exit gate:** Obtain real, source-supported, independently adjudicated scope/rules from qualified human owners; then in a different trusted channel assess rights, seal evaluator-only oracle tests and authenticate a rootless/offline sandbox and physical meters. If original intent cannot be independently established, reject Go #43 rather than filling in business rules from hindsight.
