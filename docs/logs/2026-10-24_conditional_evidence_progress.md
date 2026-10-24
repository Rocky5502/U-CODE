# U-CODE research work block — dependence-aware evidence, 2026-10-24

**Initial HEAD:** 001f4ea5f039809ac787743dbd8e43fff3e9e85d (181 offline tests). **Scientific posture:** prospective controlled study; no real model-policy effectiveness claims.

## Executive engineering outcome

Created a history-conditioned diagnostic Bellman controller and strictly segregated training-only conditional-kernel estimator, formalizing a test-dependence failure of the earlier independent-observation BES. Added a reproducible **synthetic** counterexample demonstrating different optimal test decisions under identical per-test marginal accuracy but different joint dependence. Extended Springer LaTeX and its integrity checks; no online external code execution.

## Actual deliverables

1. [src/ucode/conditional_bes.py](../../src/ucode/conditional_bes.py): exact finite tree over one candidate and historical visible test outcomes, five independent resource budgets, complete conditional likelihood contexts, no replacement by independent-action marginals. Impossible observations, duplicate test IDs, missing rows and oversized trees fail closed. Depth <=4, <=10 probes, default cap 30000 states.
2. [src/ucode/conditional_fit.py](../../src/ucode/conditional_fit.py): training-only smoothed history-conditioned class likelihoods from a *precommitted full panel*, rejecting validation/evaluation repository/fork groups, cross-model pooling, duplicate tasks, missing probes and improperly ordered evidence and oracle timestamps. A declared panel is **not** an independently verified prospective experiment.
3. [tests/test_conditional_bes.py](../../tests/test_conditional_bes.py): 20 original first-party toy tests; same marginal sensitivity/specificity with independent versus exactly redundant evidence produces different decisions. No actual model or oracle outcomes.
4. [tests/test_conditional_fit.py](../../tests/test_conditional_fit.py): 14 synthetic training-gate tests including correctly segregated complete-panel integration with conditional decision planner.
5. [examples/conditional_dependence_smoke.py](../../examples/conditional_dependence_smoke.py) and [tests/test_conditional_demo.py](../../tests/test_conditional_demo.py): one first-party toy demonstration plus two contract tests. GitHub Actions runs the example on both tested Pythons.
6. [paper/overleaf/main.tex](../../paper/overleaf/main.tex): new subsection with history-conditioned likelihood and posterior equations, prior-independent/redundant verifier counterexample, training-panel restrictions and limitations. [tests/test_paper_conditional.py](../../tests/test_paper_conditional.py) adds two manuscript integrity checks.
7. [docs/CONDITIONAL_DIAGNOSTIC_EVIDENCE_2026-10-24.md](../CONDITIONAL_DIAGNOSTIC_EVIDENCE_2026-10-24.md): explicit non-identifiability construction and study gates.
8. [README.md](../../README.md): prominent new research module and status links.

## Verified checks

At commit bfd0893c30a218b2d7a61a22de9dc9d5a203e68f: [GitHub Actions run 40092462494](https://github.com/Rocky5502/U-CODE/actions/runs/40092462494) **PASS** on Python 3.10 and Python 3.12. **219/219 offline tests passed** (181 prior + 20 conditional planner + 14 training fitter + 2 demo + 2 manuscript integrity). Normal audit and registry validation remain in CI. The exporter publishes a source-only Springer LaTeX ZIP artifact, not an authenticated live Overleaf update nor successful official sn-jnl PDF compile.

The independence/redundancy gap is not an observed LLM result. In the synthetic prior 0.5, release gate >=0.9, test sensitivity/specificity 0.8, planning price 0.01, independence assumption permits two positive tests and a contingent net expected value 0.285. Perfect correlation retains posterior 0.8 after observing both positives, so positive-cost probing has no value and the controller immediately abstains. This is a non-identifiability *construction*, not a new general theorem.

## Percentage-of-completion interpretation

**Subjective project planning estimate, not a measured performance metric:** algorithms/scaffold ~70%, literature/problem definition ~75%, dataset/provenance work ~35%, genuine model/oracle experimentation ~5%, journal manuscript readiness ~35%; overall **approximately 30%** toward defensible submission. Counts of completed unit tests or experimental protocols are not a proxy for scientific validation. The historical PR screening ledger covers **84 of 120 attempts, 83 retrieved and zero fully admitted executable tasks**. The *bulk* of outcome-producing work remains.

## Go / hold and next gates

**GO:** dependence-aware diagnostic decision reference, complete-training-panel fitting contracts, mathematical demo, regression CI, manuscript-method section.

**HOLD:** actual independently verified third-party task/functional oracle, independently calibrated patch prior and conditional action kernels, causal comparison of testing policies under real costs, model-weight revision/license approval, multi-family language runs, accepted-set risk/coverage evidence, final results/figures and journal submission. Never execute third-party source in ordinary CI; only in an audited isolated network-off nonprivileged environment.

**Next highest-value scientific gate:** choose 1–3 licensed, reproducibly runnable pre-fix tasks; review source authorship and file rights, construct sealed test oracles and a sandbox, then collect *actual* pre-outcome test panels on independently labeled training tasks. No model evaluations should be claimed before that gate.
