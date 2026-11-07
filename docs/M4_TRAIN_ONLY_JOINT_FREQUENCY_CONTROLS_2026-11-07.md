# M4 — Frozen joint-outcome frequency baseline and same-marginal controls

**Date:** 7 November 2026. **Evidence:** offline research software, input-contract checks and **invented test labels only**. No independently qualified PHP/Go executable task, authenticated evaluator oracle, model checkpoint inference, or measured search-policy effect. This is an exploratory M4 comparator, **not a ninth registered confirmatory arm**.

## Problem and why a joint baseline matters

The 2×2×2 three-way DRPA reference gives a sharp interval for expected useful-Pareto gain when only three marginal probabilities are supplied. That lower bound may be deliberately pessimistic. A falsifiable algorithmic comparison must include a baseline which **actually predicts a joint distribution**, rather than giving the proposed robust method extra information or better cost accounting.

We now implement a *minimal*, context-bucket-conditional empirical joint model with eight state probabilities. The model is **not** a strong neural feature-conditioned multivariate predictor, does **not** yet infer uncertainty from a codebase, and must not be reported as a complete state-of-the-art joint-EHVI baseline. A strong learned conditional model remains a required follow-up.

## Trusted data roles and strict inclusion contract

Each prospective training/validation row declares:

- Immutable task/candidate identity and a repository/fork **lineage group**.
- A single specified model checkpoint identity and candidate-producing intervention (`generate` or `repair`).
- A **frozen public-only context bucket** and SHA256 digest of the pre-outcome context with a timestamp *before* any training label.
- A frozen, consistent *independent* training-label protocol plus 3 individually observed binary outcomes: high reliability `R`, high safety `S`, candidate usable `V`.
- A training-label evidence reference and later label timestamp, which remain *training-side* data.

**Critical unobservability caveat:** the three outcomes are required to be jointly defined for *every* input candidate, including invalid candidates (`V=0`). If reliability/security are undefined for invalid patches, this interface must not quietly impute `R=S=0`; one needs an independently approved estimand, an explicit policy for invalid candidates, and an appropriate missing-outcome model. Reject such incomplete real observations rather than manufacture joint labels.

The fitter enforces pre-outcome-before-label order, one prospective candidate per task, no duplicate tasks, no unassigned lineage, no train/validation/evaluation mixing, a single model/action/public-bucket/labeling protocol, at least 8 train rows and 2 lineages, and **at least 2 lineages with positive and negative labels for EACH of R/S/V**. A validation scorer accepts only distinct validation lineages and hashes task IDs to reject train/validation repetition even if someone relabels the lineage string.

These are structural guards, **not authentication** of source-era spec, independent reviewer, labels, actual model inference or true lineage ancestry. Nothing is fitted from the project’s current PR discovery data, which does not contain approved labels.

## Group-balanced smoothed joint estimator

Let `j in {000,001,...,111}` be one joint R/S/V atom. For a frozen public context bucket `c`, let `n_gj` be the count of atom `j` from training lineage `g` and `n_g=sum_j n_gj`. We compute:

```text
joint_mass[j|c] = (alpha + sum_{g in G_c} n_gj/n_g) / (8*alpha + |G_c|)
               with alpha > 0.
```

Each repository/fork group contributes **total one** regardless of its number of tasks. This is equal-group-weight additive smoothing, **not** a claim of a fully Bayesian hierarchical posterior or proof of cross-repository transportability. The status is always `TRAIN_ONLY_SMOOTHED_CATEGORICAL_JOINT_NOT_ATTESTED_NOT_CALIBRATED`.

From the same eight probabilities, marginal predictions are derived exactly by summation:

```text
p = P(R=1) = sum_{j:R_high} mass[j]
q = P(S=1) = sum_{j:S_high} mass[j]
v = P(V=1) = sum_{j:V_valid} mass[j]
```

These values are used to create the public candidate proposal. The matched four-way comparator **rejects** a candidate whose (p,q,v) differ from its trained joint model, preventing a method from claiming an improvement due merely to different forecasts.

## Four policies, one candidate menu and five independent budgets

For each budget-feasible candidate action `a` with frozen support points `(r0,r1),(s0,s1)`, reference archive and five-vector resource price, we calculate on the **same** information:

| Exploratory rule | Expected gross useful-Pareto gain | Interpretation |
|---|---|---|
| Fully independent | `sum_{ijk} P(R=i)P(S=j)P(V=k)*k*g_ij` | Product of the **same three marginals** |
| Two-way DRPA | `v * min_coupling(R,S) E[g_ij]` | Robust R/S dependence, assumes independent V |
| Three-way DRPA | `min_coupling(R,S,V) E[k*g_ij]` | Worst case over all 2×2×2 couplings |
| Training-only joint | `sum_{ijk} joint_mass_ijk*k*g_ij` | Expected utility under the **fitted** joint frequency distribution |

Each rule subtracts **the identical** scalarized five-resource cost and must obey the **same** independently enforced five caps and public action menu. If all net gains are nonpositive, it chooses STOP. Ties are lexical by candidate ID. This comparison is a mathematical acquisition-only control, **not a claim that the 8 original registered agents run faithfully**.

A fitted joint model matching the three marginals must have expected useful-HVI between the sharp three-way bounds. The implementation asserts this property for every feasible action.

## Separate validation, no access to evaluation labels

The frozen model can be *scored* on held-out **validation** lineage groups without refitting. It reports an eight-class Brier score, multiclass log loss, mean marginal Brier score and per-marginal absolute reliability gap. These are **descriptive validation estimates**, not population calibration certificates, confidence intervals or test-set performance. The scoring rules are established; see Gneiting and Raftery (2007), *Strictly Proper Scoring Rules, Prediction, and Estimation*, *Journal of the American Statistical Association*, 102(477), DOI [10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437).

No evaluation group may be passed to fit or validation; the separate public release/abstain policy does not receive individual label records or hidden oracle calls. A cryptographic hash or timestamp supplied by an untrusted caller does not prove the label was independently assessed.

## Independently testable synthetic disagreement

Construct four *invented* training lineages with four 000 and four 111 labels per group. The three marginal forecasts are all `p=q=v=0.5`, but the fitted joint has strong 000–111 dependence. Compare these candidate-producing actions using the **same fitted joint**:

- `risky`: R/S outcomes 0 or 1, one token at 0.01 price.
- `stable`: R/S outcomes deterministically 0.5 each, two tokens at 0.01 price.
- Archive and reference point are both zero; candidate validity probability remains 0.5 in *both* actions.

The fitted-joint expected-gain selector can choose `risky` because its trained 111 atom probability is high, whereas worst-case three-way DRPA chooses `stable` because its worst-case gross gain is exactly `0.5*(0.5*0.5)=0.125` while risky has zero worst-case triple-event intersection. This is a **synthetic policy divergence**, not a validated optimal decision. Both could be inferior to a properly calibrated feature-conditioned model.

## Source and verification

- [`src/ucode/joint_frequency_fit.py`](../src/ucode/joint_frequency_fit.py): typed labeled train/validation contracts, group-balanced smoothed joint 8-cell model, lineage-disjoint held-out scoring.
- [`src/ucode/joint_frequency_controls.py`](../src/ucode/joint_frequency_controls.py): same-support same-marginal four-way acquisition comparison.
- [`tests/test_joint_frequency_controls.py`](../tests/test_joint_frequency_controls.py): synthetic lineages, per-class gate, strict split/test-label leakage rejection, sample imbalance, no invalid label imputation, deterministic tie and ordering, five hard costs and matched forecast controls.
- [`paper/overleaf/main.tex`](../paper/overleaf/main.tex): methods and unfilled empirical results.
- [`configs/confirmatory_sbse_protocol_2026-10-25.json`](../configs/confirmatory_sbse_protocol_2026-10-25.json): unchanged registered 6-model/8-policy design.

**Next scientific requirement:** independently admitted real training labels for all three clearly defined outcomes, a trustworthy repository-group split and pre-outcome feature generation, strong task-conditional multivariate model controls, independent genuine held-out functional/security evaluation and measured resource accounting. All remain **not yet done**.
