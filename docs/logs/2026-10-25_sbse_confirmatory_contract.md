# U-CODE execution ledger — strengthened Springer SBSE research design

**Date:** 25 October 2026. **Starting HEAD:** f173049c902612b8d3b1e4f0230329458ae00199 (315 offline tests). **Venue verified:** Springer *Automated Software Engineering* special issue *Search-Based Software Engineering in the Era of LLMs and Agentic Systems*, open call and deadline 30 January 2027.

## Concrete new scientific/engineering outputs

1. [Eight-policy six-model prospective factorial protocol](../../configs/confirmatory_sbse_protocol_2026-10-25.json). Researcher-selected six open-weight checkpoints remain included; eight competing search/verification *policies are planned*, not reported as implemented or evaluated. Primary U-CODE conditional BES vs matched identical action/search budget **without calibrated uncertainty**, with multiple ablations and strong comparator plans.
2. [Strict evaluator-side empirical contract](../../src/ucode/experiment_contract.py): frozen task × model × seed × budget × policy matrix; policy-visible terminal receipts without gold labels; independent evaluator-only verdict records with exact patch SHA256 match; each policy trace bound to task base Git SHA40, model revision SHA40, tool-access SHA256 and environment SHA256. All five measured cost dimensions must not exceed individually allocated caps; changing any matched checkpoint/tool/environment or dropping failures is forbidden. No untrusted source or models are executed.
3. [Partial-identification missingness analyzer](../../src/ucode/attrition_bounds.py): worst/best treatment-success effects with full assigned denominator, **timeouts/safety stops scored 0 and reported by type**, infrastructure errors unknown [0,1]. Conservative bounds are **not confidence intervals**. Existing [paired evaluator](../../src/ucode/evaluation.py) supports conditional wrong-release risk, coverage and repo-group bootstrap for complete validated trials.
4. [Prospective protocol gate](../../scripts/validate_sbse_protocol.py): validates all six user-selected model identities, all eight distinct named controls, primary predeclared treatment/control, entire five-component numerical cap and **zero admitted tasks/empirical effects**. Rejects NaN and infinite budgets and fractional token/test counts. Hypothetical cap/seeds cannot self-promote to frozen experiment.
5. [First-party synthetic integrity tests](../../tests/test_experiment_contract.py), [missingness tests](../../tests/test_attrition_bounds.py), [protocol tests](../../tests/test_sbse_registration.py), and [paper method tests](../../tests/test_sbse_paper_protocol.py). All results in these tests are invented controlled fixtures, **not measured coding-agent performance**.
6. [Official primary literature](../../paper/overleaf/references.bib) and [Springer main.tex](../../paper/overleaf/main.tex): RETRACE (2026 preprint), Dockerless (EMNLP 2026), SWE-Bench Pro Verified (2026 preprint); novel selection-vs-verification distinction; hashed evaluator receipt equation; failure attribution/bounds equation; explicit eight-policy planned comparison; no fake RQ results. [Research protocol memo](../SBSE_CONFIRMATORY_EVALUATION_AND_FALSIFIERS_2026-10-25.md) and [README](../../README.md) updated.
7. GitHub Actions now validates this prospective plan and continues exporting the `ucode-overleaf-sources` LaTeX source artifact. **No authenticated live Overleaf update or publisher-class PDF compilation.**

## Verification, novelty and blockers

The last previously verified main commit had 315/315 standard-library offline tests passed on both Python 3.10 and 3.12. A successful intermediate new-contract run reported 378 tests; the final head must be checked after all doc and integrity-test commits. CI does **not** run external PR code, models, hidden oracles or any paid GPU.

Latest work confirms that independent verification and leakage-safe benchmarking are **already** active research topics. Novelty cannot rest on an established Bellman recursion or simply choosing tests. Need **real independent task results** showing that calibrated resource-allocation actions yield higher verified full-task success at matched five-vector budgets and meaningful coverage than strong uncertainty-free search and selective verifier baselines.

**Zero qualified executable benchmark tasks; zero genuine six-model inference results; no measured model reliability benefit.** The two original PHP and Go PR admission dossiers remain blocked on 16 open external authorization, rights, oracle and sandbox gates. RETRACE and Dockerless are prospective comparators, not faithful code already copied/implemented.

## Next actual experimental priority

Independently approve a file-rights-cleared frozen pre-fix task, a separate sealed functional oracle and a rootless network-disabled resource-limited runner. Freeze model/tokenizer checkpoint identities/versions and an affordable pilot budget using actual measured device/runtime capabilities. Implement and fidelity-audit the uncertainty-free matched-search controller. Execute a small fully paired pilot, report all failures and then power/precision plan the journal matrix. Negative effects must be preserved.

**Research integrity:** no made-up benchmark, model inference, acceptance, code execution, statistical significance, completed journal submission or assurance certificate.
