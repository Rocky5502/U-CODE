# U-CODE — post-terminal ITT, release and missingness accounting

**29 October 2026. Stage: FIRST-PARTY SYNTHETIC VALIDATION ONLY.**

The aim of this module is to protect the eventual Springer RQ3
evaluation from incorrect denominators, selectively dropping crashed
agent attempts, or declaring that a system which never releases code has
`0%` observed wrong-release risk.

## Sources and separation

- Canonical preregistered assignments: `FrozenStudy`.
- One frozen policy-run receipt for **every** assigned policy/model/task/
  seed/budget cell, checked by `audit_confirmatory_run_matrix`.
- An evaluator-only verdict for each **released** patch, matched to
  the actual emitted patch SHA256; never sent into the decision policy.
- Five reported resource dimensions: `tokens`, `test_calls`,
  `gpu_seconds`, `cpu_seconds`, `wall_seconds`.
- New `src/ucode/postterminal_accounting.py` consumes those typed
  records **only after policy termination**. It reuses the existing
  `paired_effect_attrition_bounds` rather than inventing a new
  single-number comparison.

The code has **no API** that imports GitHub repository source, model
weights, oracle secrets, or executable commands. This is deliberately
an analysis module, not the prospective task executor.

## Definitions and conditional-risk caveat

For each arm, let N = number of assigned cells; r = known releases;
s = oracle-verified successful releases; w = oracle-verified incorrect
releases; u = infrastructure failures with completely unknown outcomes.
The exact observed categories are **release, abstain, timeout,
safety_block and infrastructure_failure**.

| Quantity | Worst/best envelope when infra failures remain unknown | Meaning |
|---|---|---|
| Full-task ITT success | [s/N, (s+u)/N] | Unknown infrastructure outcomes could be successes; known timeout/stop/no-release are nonsuccess |
| Release coverage | [r/N, (r+u)/N] | Unknown infra outcomes might or might not have released |
| Wrong-release risk of known released patches | w/r if r>0; else **null** | Descriptive known-release subset only |
| Potential conditional wrong-release risk | [w/(r+u), (w+u)/(r+u)] if r+u>0; else **null** | Sensitivity envelope, **not** risk certification |
| Mean *reported* resources | Each separately summed and divided by N | Not independently measured just because fields are labeled measured |
| Paired treatment-minus-control ITT effect | Existing task/model/seed/budget matched worst/best differences | Infrastructure errors not silently excluded |

The risk fraction conditioned on release is not a primary full-task
success metric. In particular, if r=0 and u=0, the conditional
wrong-release risk is **undefined**, not zero. If r=0 and u>0, the
observed-only risk remains undefined even though potential risk can
range from 0 to 1.

These are mathematical sensitivity bounds with unspecified dependence;
they are **not** frequentist confidence intervals, Bayesian credible
intervals or distribution-shift guarantees. When both compared arms
are complete with no outcome attrition the original repository-lineage
bootstrap can produce a descriptive paired interval. If any registered
arm has incomplete outcome, this reference conservatively suppresses
the bootstrap/point estimate; an infrastructure-failure bound remains.

### Synthetic mechanism check

Run:

```bash
python -m scripts.smoke_postterminal_accounting
python -m unittest discover -s tests -v
```

The demo invents **two artificial tasks** with one fabricated
successful release, one fabricated wrong release, one policy timeout
and one infrastructure failure. It demonstrates an ITT paired
difference sensitivity interval [0, 0.5] instead of a falsely precise
effect. It labels all fixture verdicts as **fabricated**. Nothing was
actually executed or independently evaluated.

Adversarial tests reject missing evaluator responses, mismatched
released patch digests, duplicate/unassigned policies, missing matched
task cells, checkpoint drift, and gold-label injection. Tests also
assert undefined risk for all-abstain policies and nonintegral
*mean* token/test-call usage even though individual counters are
integers.

## Remaining scientific authorization gates

The existing `PolicyRunReceipt.actual_costs_measured`, evaluator
SHA256 strings and named source labels are assertions from the
caller, **not** independent cryptographic attestation. Real empirical
results remain prohibited until: an independently qualified pre-fix
repository task; file-specific rights and source-era issue
specification; hidden functional oracle; verified isolated runtime;
independent five-resource metering; frozen model/checkpoint and tool
access; independently verified attribution; group-safe splits;
and recorded protocol-level reviewer approval.

Paper source `paper/overleaf/main.tex` describes these formulas
in the Methods section only. **Results have no measured claims,
full-model experiments or risk certificates.**
