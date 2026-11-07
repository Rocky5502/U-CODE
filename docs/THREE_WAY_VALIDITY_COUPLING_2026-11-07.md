# U-CODE M4: Three-way reliability–safety–validity coupling audit

**Date:** 2026-11-07. **Class:** bounded source-only mathematical reference; zero project LLM inference, zero admitted external tasks, zero separately sealed functional gold, and no measured code-repair gain. This is an *exploratory extension* to DRPA, not a ninth registered confirmatory policy.

## Why the earlier DRPA score was incomplete

[The 2026-11-06 DRPA reference](DRPA_DEPENDENCE_ROBUST_ACQUISITION_2026-11-06.md) permitted arbitrary dependence between a candidate's predicted **reliability R** and **safety S**, but multiplied the lower/upper EHVI by a separately predicted **validity probability v**. That multiplication presupposes that V (whether the new candidate can be accepted/used) is *independent* of both objective outcomes. Such independence can fail in real software changes: invalid patches and regressions may co-occur with safety/security defects.

The new `src/ucode/joint_validity_acquisition.py` drops that specific assumption. The resulting guarantee is exact *only for the supplied three Bernoulli marginal forecasts and four specified Pareto objective support points*. It is NOT a frequentist guarantee, not a fitted uncertainty model and not a new general-purpose optimal-transport theory. Fréchet classes and sharp coupling bounds are established mathematical concepts (e.g., Bartl et al., *Marginal and Dependence Uncertainty: Bounds, Optimal Transport, and Sharpness*, SIAM Journal on Control and Optimization, 2022, DOI 10.1137/21M144709X).

## Precise finite-support setup

Let R take `r0,r1`, S take `s0,s1`, and V be binary with `V=1` meaning the generated candidate is usable. Freeze the three *marginal* forecasts BEFORE seeing evaluator outcomes:

```text
P(R=r1) = p,       P(S=s1) = q,       P(V=1) = v.
```

Define `x_ijk = P(R=ri, S=sj, V=k)` for 8 binary atoms. Every feasible joint distribution is an element of the polytope:

```text
x_ijk >= 0                 for all i,j,k in {0,1}
sum_ijk x_ijk = 1
sum_jk  x_1jk = p
sum_ik  x_i1k = q
sum_ij  x_ij1 = v
```

For a public candidate Pareto archive `A` and a predeclared reference point, define the candidate-only increment:

```text
g_ij = HV(A union {(ri,sj)}) - HV(A) >= 0.
f_ijk = k * g_ij              (invalid candidate contributes zero).
```

Our exact finite LP is:

```text
L = min_(x in admissible 2x2x2 couplings) sum_ijk x_ijk f_ijk
U = max_(x in admissible 2x2x2 couplings) sum_ijk x_ijk f_ijk.
```

The constraint matrix has **rank four** and eight variables. Every extreme point has a basic feasible representation with at most four nonzero atoms; enumerating the at most **C(8,4)=70** four-column bases is therefore sufficient. The code solves every nonsingular 4x4 system with **exact rational Gaussian elimination**, checks nonnegativity, deduplicates degeneracy, and computes the four objective gains with exact decimal-rational 2D Pareto area. This is exact *relative to the user-supplied decimal values* and the bounded 2x2x2 support—not relative to unknown real-world parameters. No numerical LP package, RNG, or sampling is needed.

The model-conditional maximin intervention criterion is

```text
a* = argmax_(generate/repair a, five-cost-vector(a)<=remaining)
          {L(a) - unit_prices dot five-cost-vector(a)}
only if the best score is strictly positive, else STOP.
```

Verification-only test/retrieve/static-analysis actions do not create a Pareto point; existing evidence-value controllers remain responsible for them. Actions obey five hard resource caps independently. Candidate-specific validity is **not** the same as independently measured full-task success; eventual empirical labels and preprocessing must define it before inference.

## Independent mathematical falsifiers

For an empty archive, zero reference point, and `r0=s0=0, r1=s1=1`, the improvement equals one **only when R=S=V=1**. Standard three-event intersection inequalities therefore give an *independent closed-form oracle*:

```text
max(0,p+q+v-2) <= E[V*DeltaHV] <= min(p,q,v).
```

We test all **125** combinations of `p,q,v in {0,.25,.5,.75,1}`, including degenerate 0/1 marginals. Each computed extremal witness is independently checked for 8 nonnegative atoms, normalization, and all three supplied marginal identities. Additional falsifiers check 2-event reductions, the old 2-way result when `v=1`, exact nonzero-reference geometry, tie behavior, admission of no diagnostic actions, each of five hard resource caps, invalid input and nonpromotion of gold labels.

**Reversal that the original 2×2 DRPA misses:** let `p=q=v=.7`, `r0=s0=0`, `r1=s1=1`, zero archive/reference, and an action cost of two tokens at 0.1 per token.

| Mathematical action audit | Old 2×2 R/S robust + independent V | New 2×2×2 arbitrary R/S/V coupling |
|---|---:|---:|
| Predicted worst-case gross new-patch HVI | `.7 * (.7+.7-1) = .28` | `.7+.7+.7-2 = .10` |
| Scalarized planning cost | `.20` | `.20` |
| Lower net HVI | **+.08** | **−.10** |
| Candidate-producing decision | **Generate** | **STOP** |

The new ambiguity set contains the old independent-validity ambiguity set, so its **lower bound cannot be larger and upper bound cannot be smaller**. This is proved for the finite LP and checked by tests. The example illustrates **sensitivity of decisions to dependence assumptions**; it does *not* establish that STOP is better than generating a real patch. An overconservative robust policy could be substantially worse than a well-calibrated joint model.

## Inspectable code and CLI-independent tests

- `src/ucode/joint_validity_acquisition.py`: `bound_joint_validity_hvi`, `choose_joint_validity_action`, exact witness atom weights, old-score comparator, deterministic ties/abstention.
- `tests/test_joint_validity_acquisition.py`: independent closed-form oracle for 125 three-event configurations, additional action/gate falsifiers.
- `docs/G5_M4_REAL_PILOT_ACTIVATION_2026-11-06.md`: separately enforced source-era admission and hidden oracle requirements.
- `configs/confirmatory_sbse_protocol_2026-10-25.json` stays unchanged (six selected model slots; eight policy slots; existing primary contrast).

From the checked-out repository root:

```bash
python -m unittest discover -s tests -p "test_joint_validity_acquisition.py" -v
python -m scripts.compile_pilot_preflight --require-ready
# The second command must still exit code 2: no independently admitted real task.
```

## Novelty boundary and meaningful next experiments

**Not novel:** LP vertex enumeration, Bernoulli Fréchet coupling, optimal transport over marginal ambiguity, Pareto hypervolume, Bayesian acquisition, code-agent verification, budget accounting and abstention.

**Potential contribution needing empirical corroboration:** a *coding-agent action-routing study* of how reliability–safety–validity coupling misspecification affects the **choice to generate/repair or refrain under five matched resource caps**, with frozen forecasts and independently sealed task correctness. The methodology is additionally valuable if it identifies harmful conservatism or supports negative outcomes.

**Required falsifiers before a strong ASE claim:**
1. Fit validity, reliability and safety marginals on lineage-disjoint labelled training tasks; validate predictive meaning and three-way correlations.
2. Compare original independence-EHVI, 2-way R/S DRPA with independent validity, **learned joint 3-way EHVI**, and 3-way sharp maximin against exact matched candidate proposals/resource budgets.
3. Predeclare reference point, cost prices, budget level, task family split and exploratory versus registered confirmatory endpoints. Never tune parameters to a held-out oracle.
4. Report coverage, wrong-release risk, independent full-task ITT success and actual five-resource costs, with cluster-aware uncertainty and null/negative effects.
5. Stress wrong marginals, discretization loss, harmful STOP actions and alternative dependence constraints; no risk certificate without validated statistical assumptions.
6. Keep zero real-task/zero model inference status until independently authorized source/rights/oracle/runner gates pass.

Scientific interpretation: this change **removes one unjustified independence assumption from the bounded mathematical reference**, not the larger problem of fitting accurate marginals or proving real software quality.
