# S04 — Two-order conditional evidence coherence and robust VOI falsification

**9 November 2026 · Source-only scientific audit · No real model inferences or admitted executable tasks.**

Related [Sprint S04 issue #64](https://github.com/Rocky5502/U-CODE/issues/64). U-CODE already includes one-step scenario-robust evidence acquisition, finite-horizon history-conditioned Bayesian updates and explicitly limited multi-candidate dependence assumptions. This work addresses a **new necessary consistency gate** for the *input likelihoods* and hardens a separate terminal-only decision path.

## Finding: a valid-looking conditional table can imply contradictory joint observations

The original `ConditionalKernel` rejected out-of-range probabilities, duplicated rows and repeated action IDs. It did **not** ensure that two diagnostic actions could be observed in either order without changing the implied probability of the same joint event.

For current *visible* history `h`, proposed diagnostic IDs `a, b`, observed Boolean signs `x, z` and fixed latent correctness class `Y`, a common joint observation model requires:

```text
P(a=x | Y,h) * P(b=z | Y,h,a=x)
 =
P(b=z | Y,h) * P(a=x | Y,h,b=z)
```

The equality is required for each of the two latent classes and all four pairs of signs. For two actions this creates **eight event-class checks**. This does not assert that the latent label is observed during inference: the conditional probabilities are untrusted TRAIN-only/hypothetical model inputs, never independent hidden-evaluator labels supplied to the controller.

One inconsistent model can be constructed with root `P(a+|Y=1)=P(b+|Y=1)=0.8` and a copied, deterministic second-action relationship, but an edited row `P(b+|Y=1,a+)=0.1` instead of the required `1.0`. The joint probability for `a+,b+` then differs across acquisition order by `0.72` in the acceptable class. This is **an explicit mathematical counterexample using invented probabilities**, not a measured failure rate of an LLM.

## Implemented source boundaries

- [Bounded necessary two-order audit](../src/ucode/conditional_kernel_coherence.py) enumerates all registered two-step diamonds rooted at available *visible* histories of length at most three. It checks both latent classes and four joint outcomes, returns source-only discrepancy witnesses and detects missing conditioning paths. A sparse table is **INCOMPLETE**, never casually reported coherent.
- `fail_on_incoherence=True` rejects contradictory supplied conditional probabilities; `fail_on_incoherence=False` permits a **review-only counterexample report**. `require_complete=True` rejects missing opposite-order contexts, including a model whose supplied records allow only one order.
- [Conditional BES](../src/ucode/conditional_bes.py) now exposes `require_order_coherence=True` as an **opt-in strict gate** before purchasing a diagnostic when multiple action orders are available. It remains **off by default** for backward-compatible analytical and partial training experiments. A future real experiment must predeclare when strict path coverage is required; without it, the original planner still fails on a missing *reachable chosen-order* row but may not examine unchosen alternative orders.
- `ConditionalProbe` now rejects reserved terminal `release`/`abstain` IDs, avoiding a diagnostic whose identifier is indistinguishable from a terminal outcome. Both probes and conditional states require typed five-dimensional budget objects rather than malformed dictionaries.
- The [scenario-robust one-step decision](../src/ucode/scenario_robust_evidence.py) now checks its state, frozen resource prices and `ReleaseRule.unit_cost_penalty == 0` **before** returning even a terminal-only recommendation. Previously, with no feasible probes, the function could skip the once-only-cost guard and return an apparently valid decision under a misconfigured double-cost model.

This is a **local two-order necessary condition**, not a globally sufficient condition for a coherent full joint distribution over arbitrary long diagnostic histories. It does not establish calibrated probabilities, observed action-order randomization, source provenance, conditional independence, general optimal planning or absence of hidden label leakage. A full experiment still needs independently authenticated train-only provenance and appropriately collected factorial diagnostic panels.

## Strict example, offline only

```python
from ucode.conditional_bes import ConditionalState, ConditionalProbe, plan_conditional
from ucode.conditional_kernel_coherence import audit_conditional_order_coherence

# k is a hypothetical or independently train-fitted ConditionalKernel.
# Use a separate approved source for k; no hidden evaluator labels.
audit_conditional_order_coherence(k, ("probe_a", "probe_b"), require_complete=True)
# The following opt-in planner preflight is available for full-order kernels.
# plan_conditional(state, probes, k, prices, rule,
#                  require_order_coherence=True)
```

## Adversarial first-party verification

[22 first-party tests](../tests/test_conditional_kernel_coherence_s04.py) include independent exact Fraction chain-rule cross-checks, contradictory and coherent independent/dependent kernels, missing alternative order rows, strict planner refusal, reserved action names, malformed typed budgets, finite-scenario decision validation even when no action is affordable, and a fixed rational one-step robust regret witness. Hard budget checks exercise **all five individual resource dimensions**, not one scalar price.

```bash
python -m unittest discover -s tests -p 'test_conditional_kernel_coherence_s04.py' -v
python -m unittest discover -s tests -p 'test_conditional_bes.py' -v
python -m unittest discover -s tests -p 'test_scenario_robust_evidence.py' -v
python -m unittest discover -s tests -v
```

**Falsifiable distinction:** For an existing candidate with prior one-half, an invented perfect diagnostic with cost 0.01 has expected net improvement 0.49, whereas an invented noisy diagnostic with both posterior branches below the 90% release threshold has improvement -0.01. The maximin controller refuses the diagnostic when both frozen scenarios remain plausible. This witnesses finite-scenario robustness, **not** real-world risk coverage or calibration.

## What still blocks measured research

All numerical examples above are invented. They do not involve independent source rights, Go #43 or PHP #104 functional oracle evidence, actual repository repair, six qualified model checkpoints, physically measured hard resources, rootless isolated execution, or a valid effect/CI. The remaining full six-model × eight-policy confirmatory study and all its source-era approvals are still pending.

This update to `paper/overleaf/main.tex` is a GitHub source change, not verified sync to the online Overleaf editor.
