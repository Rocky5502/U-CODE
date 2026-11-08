# S02 — Paired attrition sign and wrong-release denominator falsification

**9 November 2026 · FIRST-PARTY SYNTHETIC / POSTTERMINAL-ONLY. NOT A REAL MODEL TRIAL.**

Related [sprint task S02](https://github.com/Rocky5502/U-CODE/issues/62). This work reuses the original paired run-matrix audit and [postterminal accounting](../src/ucode/postterminal_accounting.py). It does **not** replace the registered primary endpoint, change the eight policies, authorize Go/PHP execution, authenticate an oracle, or add an observed model result.

## Scientific question and finding

A single reported treatment-minus-control effect can be misleading if a failed runner silently disappears from a denominator or if failures are disproportionately concentrated in one arm. The existing code correctly reports the worst/best interval for missing infrastructure outcomes, but did not provide an **independently cross-checked, sign-aware and arm-specific** explanation of that interval.

The new [attrition-sign audit](../src/ucode/attrition_sign_sensitivity.py) derives the envelope again from arm-level **integer** counts and checks that it exactly agrees with the existing paired estimator. This makes an asymmetric missingness pattern visible and detects future denominator drift. It avoids interpreting an interval that includes zero as proof of a positive treatment effect.

For each frozen matched task–model–seed–budget assignment, a released patch is scored with a terminal evaluator-only Boolean verdict. Verified nonrelease (abstain, timeout or safety stop) contributes zero to **full-task success**, but remains in the assigned denominator. An **infrastructure failure** is treated as binary outcome missingness, with possible success 0 or 1, and is never assigned a convenient invented label.

Let `N` be the **original paired assignment count**; `s_T, s_C` are known verified successful releases and `u_T, u_C` are infrastructure-missing cells for the selected treatment and control arms. Under unrestricted binary completion of unknown cells:

```text
lower_effect = (s_T - s_C - u_C) / N
upper_effect = (s_T - s_C + u_T) / N
interval_width = (u_T + u_C) / N
```

This **worst/best partial-identification interval is not a confidence interval or significance test**. When `u_T = u_C = 0`, full-task success is arithmetically point identified, even if known timeouts or safety stops still cause the conservative complete-case bootstrap to remain suppressed. Positive, negative and zero effects are reported as separate **attainable signs** based on the *integer* endpoints. Every intermediate integer numerator can be reached by some unrestricted binary completion; a positive result is only sign-robust when the **lower endpoint is strictly positive**. An exactly zero fixed effect is sign-robust but is not an improvement.

### Why a rate of zero can be misleading

For the **conditional wrong-release risk** of a single arm, let `r` be the number of released patches with Boolean evaluator verdicts, `w` the known wrong releases, and `u` the infrastructure failures. Observed wrong-release risk is `w/r` when `r > 0`, and **undefined when `r = 0`**. Conditional on some patch eventually being released, the potential wrong-release interval is:

```text
risk_lower = w / (r + u)
risk_upper = (w + u) / (r + u)
```

This is reported **only when `r + u > 0`**. If both are zero, conditional risk is undefined, not zero. If `r = 0, u > 0`, observed-only risk remains undefined, while potential future risk can vary from 0 to 1. A failure that produced **no release** is not silently treated as a correct release.

## Falsifiers and cross-checks

[19 new adversarial tests](../tests/test_attrition_sign_sensitivity.py) cover:

- Both arms missing (positive/zero/negative effect all attainable), treatment-only missing, control-only missing, two unknown cells in each arm and sign robustness.
- Independent integer numerator checks for **every** category of a single matched pair (six terminal states per arm).
- Independent **exhaustive** enumeration of `3^u` counterfactual release states for small `r,w,u` configurations, confirming the **sharp conditional wrong-release envelope** without treating a no-release realization as `0/0 = 0`.
- Exact assignment counts when a third policy fails, category conservation, known timeout/safety zero-success semantics, and explicit suppression of the original complete-case bootstrap when its conservative policy disallows it.
- Rejection of missing/extra evaluator verdicts, corrupted released-patch SHA, missing assigned cells, unregistered policy names and exceeding **each of five separate resource caps**.

First-party tests use invented task names, evaluator verdicts, per-policy patch hashes and resource observations; their values are mathematical fixtures, **never** empirical U-CODE success or reviewer evidence.

```bash
python -m unittest discover -s tests -p 'test_attrition_sign_sensitivity.py' -v
python -m unittest discover -s tests -p 'test_postterminal_accounting.py' -v
python -m unittest discover -s tests -p 'test_attrition_bounds.py' -v
python -m unittest discover -s tests -v
```

The new function reads **only caller-supplied postterminal typed evaluator records** through the existing protected analysis contract. The report includes no raw oracle artifact digests, patch content, weights, user credentials or third-party source. All authentication flags remain **false**. A structurally valid input is not proof that any real inference, benchmark task, reviewer approval, physical budget meter, executable sandbox or functional oracle exists.

## Remaining evidence barriers

The original 10 scientific milestone exit gates remain subject to independent proof. In particular, the Go #43 and PHP #104 review pilot still has 16 of 16 external admission gates pending, zero real qualified tasks, zero sealed independent functional oracles and zero qualified six-model checkpoints. The six-model × eight-policy real trial is **not** complete. GitHub manuscript edits update source files only; no live Overleaf synchronization is claimed.
