# U-CODE — Task-scoped oracle identity across matched policies (3 November 2026)

**Scope:** first-party structural evaluation-integrity audit. **Not an independent oracle, sealed test suite, verified security boundary, real task, LLM inference, calibration experiment, or measured policy improvement.** The two public PHP/Go leads remain unadmitted, with independent review and execution gates pending.

## Defect and correction

The prior `audit_confirmatory_run_matrix` ensured each evaluator verdict targeted the same released patch digest as its corresponding terminal policy receipt, but **did not require the hidden oracle identity to remain fixed across releases of the same task**. If policy A were scored with one test artifact and policy B with another, the records could pass all previous structural checks, and an apparent paired treatment effect would conflate policy performance with evaluation difficulty.

The evaluator-side audit now requires:

1. **One task, one declared evaluator oracle.** Every `EvaluatorVerdict` for a given `task_id`, regardless of policy, model, seed or budget, must carry the identical `oracle_artifact_sha256`. Different tasks may legitimately have different oracle identities.
2. **Deterministic repeat-label consistency.** If the *same* patch digest is released for the *same* task in multiple cells, it cannot receive contradictory Boolean correctness labels under the same fixed oracle. Genuine flaky or stochastic evaluations require a separately specified repeated-trial protocol and should not be silently reported as deterministic correctness.
3. **Existing evaluator-only separation.** Verdicts cannot target abstentions, unassigned runs or the wrong released patch. Outcomes remain post-terminal and are not passed to the agent/policy.

The fixture in `tests/test_experiment_contract.py` previously assigned the same placeholder patch digest to policy-generated synthetic outcomes of opposite correctness. That fixture itself violated the stronger scientific contract. Synthetic patch identities are now explicitly distinct per task/model/seed/policy except in the deliberately constructed repeat-patch tests.

## Falsifiers

Adversarial first-party tests attempt an oracle digest swap for one policy, one model and one seed; contradict correctness for an identical task+patch; allow a *consistent* duplicate patch across arms; and allow different oracle artifacts for different tasks. All tests are hypothetical; the main repository's Python 3.10 and 3.12 workflows validate the change.

## Boundary limitations

- **Agreement does not authenticate a hash.** If a malicious evaluator rewrites *all* task-level oracle references and verdicts together, this structural audit alone cannot detect it.
- Even with one digest per task, **a hash cannot prove an oracle was independent**, sealed before model outputs, correct, legally usable, or inaccessible to the policy. The real pilot requires a separately trusted, independently authenticated *pre-outcome* task/oracle commitment and physical policy/evaluator separation.
- Only *released* patches produce verdicts; an all-abstain task has no observed oracle digest to compare here. The study-wide precommitted task registry is a separate mandatory real-study admission gate.
- This code does not solve drift due to environment, nondeterministic tests, cross-lineage contamination or unsafe third-party execution.

## Reproduce

```bash
python -m unittest discover -s tests -p 'test_experiment_contract.py' -v
python -m unittest discover -s tests -p 'test_postterminal_accounting.py' -v
python -m unittest discover -s tests -v
```

**Status:** scientific evaluator invariant strengthened; empirical readiness, model execution and independent task admission **unchanged at zero**. See [issue #7](https://github.com/Rocky5502/U-CODE/issues/7), [issue #2](https://github.com/Rocky5502/U-CODE/issues/2) and the [3 November checkpoint](UCODE_RESEARCH_PROGRESS_2026-11-03.md).
