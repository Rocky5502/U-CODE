# U-CODE research block — G1 novelty, G5 problem formulation

**Date:** 2026-10-24  
**Session mode:** user-triggered execution, no background execution  
**Baseline main SHA:** `93cbb4a604bbc2c824179a7d348b688eee57a89e`  
**Primary related issues:** [#4 SBSE acquisition](https://github.com/Rocky5502/U-CODE/issues/4), [#6 journal artifact](https://github.com/Rocky5502/U-CODE/issues/6)  
**Roles:** PI, SBSE theorist, Bayesian uncertainty researcher, security/risk reviewer, empirical SE reviewer, reproducibility engineer, Springer paper editor.

## Completed and auditable

1. **Novelty review:** 23 entries with verified canonical source URLs, priority and required baselines in [literature matrix](../../literature/novelty_matrix_2026-10-24.csv). Close overlap includes SWE-Verifier, SWE-Search, GA4GC, SWE-Replay, ExecCritic and uncertainty-only self-correction negative findings. Most sources were checked at primary abstract/metadata level; selected close competitors were inspected at method/text level. A full systematic literature review is **not** claimed.
2. **Formal design:** [novelty and problem specification](../FORMAL_PROBLEM_AND_NOVELTY_2026-10-24.md) defines immutable task/held-out oracle, admissible state, 5-dimensional cost limits, release vs abstention, accepted-set conditional wrong-release risk, minimum coverage, Bayes action transitions, Bellman target, diagnostic EVSI and candidate-generation EHVI.
3. **Corrected theoretical flaw:** [src/ucode/acquisition.py](../../src/ucode/acquisition.py) rejects information-only `test`, `retrieve`, `static_analysis` and `abstain` as fictitious new candidates. [src/ucode/voi.py](../../src/ucode/voi.py) is a small **analytical** one-step Bayesian diagnostic reference with explicit pre-outcome sensitivity/specificity and budget; it is not an empirically fitted model.
4. **Analytical negative example:** strict risk release gate can make signed post-diagnostic evidence value negative even though ordinary unconstrained VOI cannot be negative when signals may be ignored. Concrete worked case is in the formal memo; protected with tests.
5. **Journal manuscript:** [Springer main.tex](../../paper/overleaf/main.tex) now contains substantive Introduction, Related Work, Definitions, budgeted Bellman/EVSI mathematics, risk/coverage estimands, methodology and honest limitations, with [14 source-verified bibliography entries](../../paper/overleaf/references.bib). No paper result numbers invented. Official Springer publisher class is not vendored or compiled here.
6. **Regression tests:** new `tests/test_voi.py`, `tests/test_paper_integrity.py` and corrected `tests/test_acquisition.py` cases, plus updated synthetic example. Exact Python 3.10/3.12 CI links should be checked on most recent commit.

## Findings status

- **Established from published papers:** search, verifier choice, multiobjective optimization, and uncertainty-guided coding are pre-existing ideas. This is a major originality threat, not an U-CODE result.
- **Proved in a controlled mathematical reference:** exact Bayesian posterior updates and signed EVSI under declared hypothetical inputs. A negative signed EVSI is possible under a forced posterior hard release gate. No real software labels used.
- **NOT established:** originality of a new controller, empirically improved success, calibrated/guaranteed risk under distribution shift, multilingual model performance, true 12-language corpus, or executable task integrity.

## Hardest open questions

- Do available visible diagnostics have predictable likelihood ratios across tasks, model families and language shifts?
- Does calibrating them alter *which action* to buy, beyond mere task difficulty and available budget?
- Does joint heterogeneous-intervention allocation outperform SWE-Verifier-style selective verification, search without uncertainty and a fixed test schedule when all resources are charged?
- Can a risk gate maintain meaningful coverage instead of trivially abstaining? Can selective risk be estimated honestly after adaptive selection and cluster grouping?
- How to distinguish this central contribution from the user's CALM-SE intervention work and OpenCoderX-E correlation-aware search?

## Next single actionable work block

1. **G2/G4:** prepare first safety-reviewed independently executable task slice and test leakage protocol; do not run arbitrary repositories on the host.
2. **G5/G6:** implement a full transition kernel that gives comparable terminal utility to test/retrieve vs generate/repair, with explicit vector feasibility and oracle-free pre-outcome parameter fitting.
3. **G8:** freeze exact no-uncertainty controller, selective verification and fixed testing baselines on shared task/seed/budget manifests.
4. **G10:** only then evaluate actual correctness and risk, report null results.

**Stop/go:** GO for formal and prototype research, HOLD on empirical or submission-readiness claims. No unapproved paid compute, third-party test execution or account-level Overleaf modification occurred.