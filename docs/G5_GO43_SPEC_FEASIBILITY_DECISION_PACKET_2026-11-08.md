# Go #43 independent specification feasibility: conditional witnesses and decision dependencies

**8 November 2026 — Source-era reviewer preparation, NOT a real executable task, test oracle, security attestation or signed review.**

## Purpose and source anchors

The source-pinned Go settlement candidate is `PlayHuai/eighty-point-huai-an` PR #30 / issue #29, proposed **declared microtask**, original base `ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a`.

Two **pre-fix** document objects were observed at the same original Git tree:

| Document | Original Git blob | Primary relevant clauses |
|---|---|---|
| [`docs/design.md`](https://github.com/PlayHuai/eighty-point-huai-an/blob/ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a/docs/design.md) | `b566ca7627b6518670a866a6a637bd5257e947f4` | §3.2 point settlement, multipliers and zero-floor; §3.3 rank; §7 atomicity |
| [`docs/淮安80分业务规则.md`](https://github.com/PlayHuai/eighty-point-huai-an/blob/ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a/docs/%E6%B7%AE%E5%AE%8980%E5%88%86%E4%B8%9A%E5%8A%A1%E8%A7%84%E5%88%99.md) | `e71288e3127cb66f2471a5ddd2800092db0552cc` | §8.4 spring/two-game outcome; §9 game/rank dynamics |

The design expressly references the business rules as authority. **No independent human has confirmed their normative sufficiency for this particular microtask.** The issue was created only eight seconds before the PR; no independently sealed issue-body version as of PR creation has been found. Exact Git blob identity is source history, **not** authorization, independent specification approval or an oracle. See [original two-source handoff](G5_GO43_SOURCE_ERA_ORACLE_REVIEW_2026-11-07.md).

## A: Conditional infeasibility witness — not a game-result prediction

The design requires player balances not to become negative and equal settlement credits/debits conserving the sum of points. These can be **jointly infeasible under one particular interpretation**, which we deliberately do **not** select as the game rule:

1. Each of two winners is credited a fixed nominal amount `t > 0`.
2. Each of two losers has the same nominal debit `t`, independently capped at that loser's current nonnegative balance `b_i`.
3. No third-party account, subsidy, debt, redistribution, winner-credit reduction or other compensation exists.

Then the net change of point mass is

```text
Delta = 2*t - min(b1, t) - min(b2, t)
```

For the **fictional explanatory witness** `t=5, b1=b2=2`, this gives `Delta=10-2-2=+6`. Thus fixed nominal winner credits + individually capped loser debits **cannot conserve points** in that state. If `b1=b2=5`, `Delta=0`; the witness does *not* claim a universal contradiction for every balance.

**Interpretation to resolve privately by an independent domain owner:** Is the credited winning amount adjusted to the money actually debited, is the account allowed to go negative when an explicit configuration enables it, or is there another documented mechanism? Do not infer the choice from the PR's implementation or tests. A different, independently specified interpretation could be consistent.

## B: Exact fractional nominal points — no implicit rounding rule

Design §3.2 describes a `1.5` hall multiplier and a `5`-point first-tier nominal unit. Their exact product can be `5 × 3/2 = 15/2` points, which is not an integer. An integer-only wallet requires a rounding, accumulation or unit-conversion rule that the currently examined text does not independently settle. The code uses `fractions.Fraction` and stores the exact rational string rather than guessing floor, ceiling, half-up, ties-to-even or fractional persistence.

**Reviewer decision needed:** Specify the ledger unit and observed behavior for fractional deltas (including after repeated matches), with an authoritative pre-fix section reference and a documented priority over any conflicting rule.

## Independent review dependency table

These are **conservative dependency mappings**, not approved normative requirements or executable test expectations.

| Unresolved decision ID | Prospective oracle case families affected |
|---|---|
| `ZERO_FLOOR_VS_TOTAL_CONSERVATION` | `LOW_BALANCE_SETTLEMENT`, `TEAM_DISTRIBUTION_AND_CONSERVATION`, `RANK_BOUNDARY_CROSSING` |
| `HALL_COEFFICIENT_FRACTIONAL_ROUNDING` | `HALL_MULTIPLIER_CASES`, `FRACTIONAL_HALL_MULTIPLIER`, `RANK_BOUNDARY_CROSSING` |
| `TEAM_PLAYER_SPLIT_AND_NONNEGATIVE_BALANCE` | `LOW_BALANCE_SETTLEMENT`, `TEAM_DISTRIBUTION_AND_CONSERVATION`, `RANK_BOUNDARY_CROSSING` |
| `SPRING_RULE_SOURCE_AND_SCOPE` | `A_TWO_SINGLE_VS_SPRING`, `HALL_MULTIPLIER_CASES` |
| `ATOMIC_RETRY_IDENTITY_AND_OBSERVABILITY` | `ATOMIC_ALL_PLAYER_LEDGER`, `RETRY_IDEMPOTENCE`, `RECOVERY_AFTER_RECONNECT` |
| `EXTERNAL_BUSINESS_RULES_PRECEDENCE` | **All 12** — this is a global source-authority and task-scope gate, *not* evidence that 12 cases have individually inconsistent requirements |

The goal is to help an independent reviewer identify which question blocks which prospective oracle test family. A case can be narrowed or omitted by a separately approved task-scope adjudication; the repository may not silently treat that as approval of the full PR.

## Concrete external reviewer requests

An independent reviewer should privately establish (a) the authoritative **pre-fix** task description and exact permissible settlement *micro-scope*; (b) source priority and version binding between both pre-fix documents; (c) explicit low-balance cap/conservation semantics and player/team distribution; (d) fractional multiplier representation/rounding; (e) when the first-game spring condition applies; and (f) atomicity, retry key, and recovery observability. The reviewer should be able to **reject** Go #43 rather than infer missing rules.

A distinct rights reviewer must assess file-level code reuse/redistribution permissions and source/authorship lineage. Separately responsible evaluator authors must create **private, source-era-faithful, sealed** tests without leaking expected outputs into the public research repo or policy input. Independently attested network-off sandbox, dependencies, CPU/GPU/test/token/wall-time metering and human authorization remain required before any third-party Go execution.

## Reproduce these *questions*, not any Go result

```bash
python -m scripts.export_go43_spec_feasibility \
  --output dist/go43_spec_feasibility_PUBLIC_NOT_EXECUTABLE.json
python -m scripts.export_go43_spec_feasibility --require-spec-resolved
# Second command MUST exit 2 until a separate authenticated review process.
python -m unittest discover -s tests -p "test_go43_spec_feasibility.py" -v
```

Implementation: [exact-rational witness and dependencies](../src/ucode/go43_spec_feasibility.py), [public-only exporter](../scripts/export_go43_spec_feasibility.py), [adversarial tests](../tests/test_go43_spec_feasibility.py). GitHub CI exports a public status packet containing **no gold answers, external source contents, reviewer identities or privileged approvals**. CI tests a first-party hypothetical witness only; it does not run Go code, perform paid model inference, or certify the game requirements.

### Required status after this update

**Go #43 = 8/8 admission gates pending; PHP #104 = 8/8 pending; 0 independently admitted tasks; 0 independently sealed functional oracles; 0 real policy results.** The registered six-model/eight-policy/five-resource confirmatory experiment and its main comparison are unchanged. Live Overleaf remains separate from the GitHub manuscript source. No task should be promoted on the strength of this packet.
