# U-CODE joint archive BES and matched-target engineering ledger

**Date:** 26 October 2026  
**Scientific status:** offline synthetic algorithm validation only; **no empirical
LLM, third-party repository, hidden-test, or six-checkpoint experiments**.

## Motivation and fairness correction

The older `conditional_archive.py` plans diagnostics separately for each
patch, whereas `optimized_search.py` fixes a target before planning a beam
of action IDs. That asymmetry makes a claimed controlled policy comparison
premature. Both are retained for compatibility. The new matched path is:

- `src/ucode/matched_opportunities.py`: one policy-neutral menu of feasible
  `(action_id, action_kind, target_sha, nominal_cost)` alternatives. Generation
  has one target-free option; diagnostics and repair expand over **every**
  archived candidate; action IDs remain globally single-use. Deterministic
  public digest includes the remaining five-budget, attempted IDs, candidate
  identities/ancestry and nominal tool costs, **not** policy-private beliefs.
- `choose_matched_baseline`: depth-limited, bounded uncertainty-free beam
  search on that same menu. Scores use only fixed public heuristics and
  candidate-bound visible diagnostics; hypothetical future candidates are
  opportunity placeholders, not success predictions.
- `src/ucode/joint_conditional_bes.py`: finite-horizon dynamic programming
  over the whole archive, candidate-specific conditional histories, globally
  unused action IDs, five-dimensional budget and symbolic future candidate
  branches. Repair forecasts are keyed by action, target profile and exact
  visible history. Model coverage fails closed for every feasible reachable
  action-target alternative.

## Exact bounded model, not general optimality

For finite state `s`, stopping value is the maximum predicted release
utility over archived candidates or abstention zero. For depth `d`:

```text
V_0(s) = max(0, max_{x in archive} U_release(p_x))
V_d(s) = max(V_0(s),
             max_{(action,target) in common_menu(s)}
             [-nominal_planning_price(action)
              + sum_outcome P_frozen(outcome|s,action,target)
                  * V_{d-1}(transition(s,action,target,outcome))])
```

The algorithm is exact only under its supplied **candidate-factorized**
history-conditional diagnostic and producer model, bounded depth 1..4 and
bounded expansion count. It does **not** model cross-candidate latent
correlation from shared issue/model provenance. No calibrated priors, kernels,
or repair/generation transition models have yet been fitted on independently
admitted train-only data. Missing conditional rows/producer forecasts are
errors, never silent removal of a treatment action.

Symbolic future patches are typed `SymbolicCandidateKey` objects and never
real SHA256 identities. Only actual executor-produced content SHA256 can
enter `SharedSession`. After execution, a frozen scorer must assign the
*actual* patch its prior and profile; no hypothetical branch posterior is
silently imported into the real archive.

## Validation and interpretation

Added **42 synthetic/adversarial tests** in
`tests/test_matched_opportunities.py` and
`tests/test_joint_conditional_bes.py`. They exercise menu expansion,
target parity, non-active target choice, deterministic ties, symbolic
generation followed by a diagnostic, candidate evidence isolation,
parent/child ancestry, fail-closed missing kernels/producer models,
five-resource feasibility, public digest invariance, replay rejection,
and state explosion caps.

Official GitHub Actions checkpoint after algorithm and test integration:
[run 40354926845](https://github.com/Rocky5502/U-CODE/actions/runs/40354926845)
passed **532/532** tests on both Python 3.10 and 3.12. The prior checkpoint
was 490/490 on both versions. Later manuscript and README edits must be
verified on their own final HEAD workflow before declaring a final checkpoint.

These tests are constructed synthetic examples, not statistical results.
No conclusion that Bayesian allocation outperforms the uncertainty-free
baseline is justified.

## Manuscript and synchronization

Updated canonical manuscript sources:
`paper/overleaf/main.tex` and `paper/overleaf/references.bib`.
The Methods now states the whole-archive finite recursion, shared opportunity
menu, symbolic branch boundary, fail-closed coverage, factorization caveat,
and trusted metering requirement. Two verified published JMLR papers provide
methodological context: Ross et al. (2011) and Mes, Powell & Frazier (2011).

**GitHub source updates are not proof of a live Overleaf sync.** The
`scripts.export_overleaf` GitHub Actions job packages the source-only ZIP.
Live Overleaf still requires the actual project URL, edit access, and a
reviewed Git bridge or manual ZIP sync; never overwrite unreviewed live edits.

## Blockers before confirmatory RQ3

1. Independently admit rights-cleared tasks with immutable pre-fix base and
   sealed hidden correctness oracle. Existing PHP/Go pilot dossiers remain
   unapproved; do not execute third-party code.
2. Build an independently metered and **hard-enforced** runner for tokens,
   test calls, GPU seconds, CPU seconds and wall time. Current receipt costs
   are caller-reported and cannot prove physical caps.
3. Include planner CPU/wall overhead in the common resource budget or a
   preregistered equal controller-compute cap. Enforce it during planning.
4. Freeze six model checkpoint revisions, licenses, runtime/prompt templates,
   sampling opportunities and eight prospective policies before real trials.
5. Fit and freeze diagnostic likelihoods and target-specific producer
   forecasts on disjoint training repository groups. Audit misspecification
   and cross-candidate dependence.
6. Independently audit evaluator isolation, preregister estimands, matched
   seeds/budgets, cluster-aware statistics and risk/coverage thresholds.
7. Verify final Springer template compilation, reference status, and human
   authors' accurate AI-use disclosure before submission.

**Falsifier:** under matched independently measured budgets and genuinely
sealed evaluation, a tuned uncertainty-free controller may match or outperform
the conditional controller. This must remain a publishable negative outcome,
not be hidden by adaptive exclusion.
