# U-CODE — An uncertainty-blind control and static action-parity audit

**Date:** 25 October 2026. **Scientific purpose:** disprove the easy explanation that any expected improvement is caused by extra generation, testing, repair tools or looser budgets rather than **uncertainty-aware action choice**. **Status:** implemented first-party algorithmic negative control and formalized shared input inventories; no real repository task run or measured effectiveness.

## What was concretely implemented

The new [blind_search.py](../src/ucode/blind_search.py) contains a typed, deterministic controller whose available action kinds are **generate**, **retrieve**, **test**, **static_analysis**, and **repair**, with terminal **release** and **abstain**. Each action has a frozen ID, fixed priority and five-component ResourceVector cost. The state contains only candidate SHA256, attempted IDs, visible boolean observations and residual hard budget; there is deliberately no model confidence, posterior, likelihood ratio, diagnostic sensitivity/specificity or hidden evaluator verdict. The parser for an external action catalog refuses unknown keys that could carry correctness or answer information.

The policy takes the lowest-priority affordable generation action when no candidate exists, follows its predeclared diagnostic schedule when a candidate exists, and repairs after a negative visible diagnostic if one is available. After repair it invalidates *all observations on the previous candidate*. A positive visible **test** may satisfy a preregistered release trigger; positive retrieval or static analysis alone cannot do so. All used action IDs are single-use, candidate SHA256s bind diagnostic observations to code identity, and no terminal action is charged as a tool. These are **policy rules**, not a correctness certificate.

The [synthetic fixture](../configs/blind_search_synthetic_schedule_2026-10-25.json) and [replay example](../examples/blind_search_smoke.py) demonstrate this path (invented observations, fake code hashes and *nonmeasured* costs):

    generate_v1 -> retrieve_1 (positive)
                -> test_candidate_v1 (negative)
                -> repair_v1 -> test_candidate_v2 (positive)
                -> release

Illustrative token consumption is 37 of a cap of 50 and two of two test calls. Because **no independent oracle was executed**, the final release cannot be labeled correct. Reproduction is a software-control trace only.

## An action-parity audit before real comparisons

[matched_action_inventory.py](../src/ucode/matched_action_inventory.py) compares BES forecasts and blind controls as a **common set of (action ID, kind, all five individual costs)** under **identical original vector caps**. Missing/extra tools, modified diagnostic or generation cost, a changed action category and altered budget make the comparison fail. Its canonical SHA256 digest hashes sorted tool IDs/types/costs plus the initial budget.

Importantly, BES forecast likelihoods and blind-only priority ranks are *not* placed in the common digest: they are legitimately different inputs. A change in a predicted diagnostic sensitivity or candidate transition does **not** change static tool parity, and the blind controller is structurally forbidden to consume any of these fields. [Reproduce the synthetic opportunity digest](../examples/action_parity_smoke.py) without repository execution.

Static parity is **necessary but insufficient**: externally measured inference context, prompts, tokenizer revisions, terminal policies, actual tests, runtime engine differences and model access must be independently frozen and matched before claiming scientific fairness.

## What this baseline IS and is NOT

**IS:** a reproducible **fixed-schedule uncertainty-blind negative control** with explicit release gating based on policy-visible test signals, a demonstrated single-candidate generation/repair loop and fully audited vector resource and action opportunities.

**IS NOT:** a strong optimized uncertainty-free search competitor; an MCTS, RETRACE, SWE-Verifier or replay reproduction; a fitted coding-agent decision controller; an independent test verifier; an actual real-model patch trace; or a statistical demonstration that U-CODE/BES performs better.

An information-aware BES planner can consume priors, sensitivities and generative scenarios; this blind scheduler cannot. That difference makes a good *ablation* but can be an unfairly weak scientific **primary comparator**. A serious confirmatory evaluation also needs a competitive, **uncertainty-free but search-optimized** policy with comparable tuning effort, action inventory, candidate archive and verification budget. Until that stronger algorithm and its fidelity tests exist, manuscript claims should explicitly say "negative control only".

The [Springer manuscript](../paper/overleaf/main.tex) now contains a dedicated section and an action-parity equality equation. Do not confuse the source-verified PR metadata inventory (120 attempted, 62 production-source-path hints) with executable software tasks: two PHP/Go dossiers remain **unadmitted**, independent sealed oracles and isolated runners remain unavailable, and all six selected LLMs remain unexecuted.

## First-party reproduction

```bash
python -m examples.blind_search_smoke
python -m examples.action_parity_smoke
python -m unittest discover -s tests -v
```

**Highest-value next experiment:** obtain one rights-cleared independent-oracle repository task, freeze a legitimate reproducible tool environment, construct the stronger uncertainty-free search-optimized comparator, and collect genuinely paired terminal receipts for BES, the fixed-schedule negative control and the strong comparator. Retain negative results and match all five resource constraints.

**Research integrity:** No 2026-10-25 artifact from this block counts as independently verified full-task software success or risk guarantee.
