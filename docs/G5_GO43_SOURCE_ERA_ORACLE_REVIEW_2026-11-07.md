# Go #43 first-real-pilot handoff: two pre-fix requirements, no oracle or task admission

**7 November 2026 · Public reviewer planning only · DO NOT EXECUTE THIRD-PARTY GO CODE**

This is a concrete advance toward qualifying one authentic U-CODE task. It **does not** claim that any source-era specification, file-level rights, independent test, sandbox, physical meter or human reviewer has been approved. The two pre-PR documents below were inspected **read-only** from the official GitHub repository and independently tied to the **same original, pre-fix Git tree**. They are **not** copies of the post-fix PR body or PR-authored test code.

## Exact source-era identity

| Artifact | Frozen source identity | What is established |
|---|---|---|
| [Go PR #30](https://github.com/PlayHuai/eighty-point-huai-an/pull/30) | `PlayHuai/eighty-point-huai-an` | Canonical candidate #43, still **not admitted** |
| Original pre-fix base | `ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a` | Commit anchor, not evidence of a runnable build |
| Full pre-fix Git tree | `e53fb011857926632c4a4ec8752425e0f2b41559` | Public tree untruncated (88 entries) |
| [`docs/design.md`](https://github.com/PlayHuai/eighty-point-huai-an/blob/ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a/docs/design.md) | Git blob `b566ca7627b6518670a866a6a637bd5257e947f4`, **16,052 bytes** | Pre-fix design requirements, sections 1, 3.1–3.3, 6.6, 7 |
| [`docs/淮安80分业务规则.md`](https://github.com/PlayHuai/eighty-point-huai-an/blob/ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a/docs/%E6%B7%AE%E5%AE%8980%E5%88%86%E4%B8%9A%E5%8A%A1%E8%A7%84%E5%88%99.md) | Git blob `e71288e3127cb66f2471a5ddd2800092db0552cc`, **17,069 bytes** | Pre-fix business rules; the design document expressly defers to this document when rules conflict |
| `server/go.mod` | Git blob `0933c3551c51527a752bc5cca0bd47581fc304a5` | Reproducible dependency *lead*; installation/build NOT tested |
| [Original issue #29](https://github.com/PlayHuai/eighty-point-huai-an/issues/29) | Created 2026-10-23 12:18:50 UTC | Only **eight seconds before PR #30** (12:18:58 UTC). Its short current text is **not** a sealed pre-PR task specification |

The two Git blob IDs were returned from the **same base tree** and verified against a read-only file lookup. This is stronger than searching the current default branch. It is still metadata retrieval and source-history identity, **not** an independent review of how the original source author intended every settlement case. The title or PR description alone is especially insufficient because it contains post-fix solution details.

## Critical conflicts and uncertainties that an independent reviewer must resolve

1. **Zero floor versus conservation (design §3.2).** The text calls for a loss bounded at zero while also describing equal winner gains and loser deductions with conserved total. If a loser has fewer points than the calculated deduction, the two instructions can be incompatible; *do not invent an oracle rule*. Separately determine whether payouts are capped/rebalanced and at what unit (player/team).
2. **Fractional hall multipliers (design §3.2).** The design specifies hall coefficients, but does not unambiguously specify the rounding direction or tie-breaking for nonintegral player balances after applying them. The **post-PR code or PR description may not be used to resolve the pre-fix task specification**.
3. **Four-player/two-team distribution (design §3.2).** Clarify individual versus team updates, zero-balance cases and conservation invariant.
4. **Spring/two-game special result (design §3.2, business rules §8.4).** Freeze which rule and chronology qualifies for the special state; reference the original higher-priority business-rule document, not later tests.
5. **Idempotency and atomicity (design §7).** Specify observable retry identifiers, transaction boundaries and required event/ledger consequences; the vague word “idempotent” cannot by itself define a sealed test.
6. **Normative hierarchy and document versions (design introduction, business rules).** A human domain reviewer must adjudicate the original business-rule hierarchy and whether the exact pre-fix versions normatively cover the **declared settlement microtask**. Do not promote the entire PR to an independently approved task.

## Prospective independent oracle coverage: 12 topics, no expected answers

The machine-validated [public blueprint](../data/admission/2026-11-07/go43_pre_fix_oracle_review_blueprint_PUBLIC_NO_GOLD.json) supplies only case IDs and original requirement section references:

| Case family | Historical clause | Reviewer-only objective |
|---|---|---|
| GAP_TIER_EDGES | Design 3.2 | Identify agreed tier transition behaviors |
| A_TWO_SINGLE_VS_SPRING | Design 3.2, higher-priority business rules 8.4 | Distinguish ordinary versus special game termination |
| HALL_MULTIPLIER_CASES | Design 3.2 | Determine covered configurable hall multipliers |
| LOW_BALANCE_SETTLEMENT | Design 3.2 | Explicitly adjudicate capped losses |
| FRACTIONAL_HALL_MULTIPLIER | Design 3.2 | Resolve rounding semantics before oracle creation |
| TEAM_DISTRIBUTION_AND_CONSERVATION | Design 3.2 | Clarify team/player ledger and conservation |
| RANK_BOUNDARY_CROSSING | Design 3.3 | Clarify how rank follows cumulative score |
| SETTLE_ONLY_ON_MATCH_COMPLETION | Design 1, 3.1 | Ensure intermediate game events do not settle points |
| NATURAL_LEVEL_NO_DIRECT_POINT_CHANGE | Design 3.2, 6.6 | Distinguish level advancement from point changes |
| ATOMIC_ALL_PLAYER_LEDGER | Design 7 | Validate atomic consistency at transaction level |
| RETRY_IDEMPOTENCE | Design 7 | Define duplicate settlement behavior and identity |
| RECOVERY_AFTER_RECONNECT | Design 7 | Determine replay/recovery requirements |

Every public case has `stage=PROPOSED_REVIEW_ONLY_NO_TEST_CODE_OR_GOLD` and `gold_output_included=false`. The six disputed semantics are explicitly `NEEDS_INDEPENDENT_SPEC_AUTHOR_RESOLUTION`. Neither a PR-authored test nor generated arithmetic example is an independently sealed functional oracle.

## Repeatable local-source integrity test (in an independent reviewer environment)

The new [offline CLI](../scripts/compile_go43_review_handoff.py) always verifies the public metadata and issues a **no-execution** report:

```bash
python -m scripts.compile_go43_review_handoff --require-admitted
# Exit 2 is expected. No Go execution or model inference.

# OPTIONAL: a trusted human already possessing the authentic old-source bytes
# may verify BOTH original documents, without uploading their contents:
python -m scripts.compile_go43_review_handoff \
  --source-file /private/go43-original-design.md \
  --business-rules-file /private/go43-original-business-rules.md \
  --output /private/go43-read-only-git-receipts.json \
  --require-admitted
# Exit 2 remains mandatory even if both Git blob IDs match.
```

These paths are examples and are **not** claims that such local source files exist. The byte verifier computes Git's exact `SHA1("blob <length>\\0" + raw_bytes)` plus an additional SHA256 receipt, but returns **no original file text, no gold answers, no reviewer names and no task-admission approval**. The whole original documents are **not stored in this U-CODE repository**. A file digest proving consistency with the Git tree does not certify legal use, independent human review, the project's underlying semantics or safe execution.

## Review authorization needed before the first real pilot

An independent domain reviewer should freeze and approve the exact settlement **microtask** and resolve all six normative ambiguities. A separate source-rights reviewer must approve file-by-file reuse and precise attribution, an evaluator team must author and seal functionality tests *without relying on PR-added tests*, and a systems reviewer must attest the rootless, network-disabled runner with actual CPU/GPU/token/test/wall meters. The six LLM checkpoints/tokenizer templates still require license review and physical runtime verification.

All original **eight admission gates for Go #43 remain PENDING**; combined PHP/Go gates remain **16/16 pending**. This blueprint adds a legitimate, source-pinned reviewer handoff—not an accepted benchmark. The signed receipt verifier already in the repo also cannot replace independent adjudication.

**Next human-research step:** collect written author/domain decisions about score conservation versus zero floor and fractional rounding, then independently author a confidential evaluator-only oracle and build a legally approved runner. No simulated test outcome from this public plan should be described as U-CODE empirical performance.
