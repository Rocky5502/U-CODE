# U-CODE — November 2026 novelty and baseline matrix (source-checked)

**Date:** 2026-11-06. **Status:** prospective algorithmic hypothesis; NOT independent proof of novelty or real-task effectiveness. Assessments are restricted to the cited papers' accessible primary descriptions and U-CODE source; a full methods-level literature review remains necessary.

| Prior study (status) | Established contribution | Overlap / threat to U-CODE | Required falsifier or comparator |
|---|---|---|---|
| Papamarkou et al., *Bayesian Control for Coding Agents* (EMNLP 2026), [ACL Anthology](https://aclanthology.org/2026.emnlp-main.1548/) | Cost-sensitive sequential hypothesis testing; beliefs about code correctness; verify/refine/stop | **High:** Bayesian coding-agent orchestration is not a new U-CODE concept | Compare authentic finite-horizon evidence control and actual held-out correctness/cost; isolate incremental gain from dependency ambiguity |
| Liu et al., *Budget-Aware Tool Use Enables Effective Agent Scaling* / CATS (COLM 2026), [Google Research](https://research.google/pubs/cost-effective-agent-test-time-scaling/) | Joint token/tool-use accounting and budget-aware sequential/parallel scaling | **High:** cost-aware agent search and compute reallocation already exist | Equal opportunities and resource caps versus budget-aware baseline, not only unbudgeted single-pass generation |
| Ma et al., *Scaling Agentic Verifier for Competitive Coding* (ICML 2026), [PMLR](https://proceedings.mlr.press/v306/ma26av.html) | Searches for discriminative test cases, instead of uninformed random execution | **High for verification:** targeted tests and discriminative evidence are established | Show whether *when* to buy verification versus new candidates changes independently verified full-task outcomes |
| Deng et al., *Expected Hypervolume Improvement Is a Particular Hypervolume Improvement* (AAAI 2025), [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/33781) | Exact EHVI analytical/computational formulation | **High:** EHVI and its mathematics are not U-CODE inventions | Compare to strong properly implemented EHVI with joint prediction and fixed reference point |
| He et al., *Bayesian Optimisation for the Experimental Sciences* (Advanced Intelligent Systems, 2026), [Wiley](https://advanced.onlinelibrary.wiley.com/doi/10.1002/aisy.202501149) | Practical joint-posterior EHVI and multi-output predictors capturing correlated objectives | **High:** model-aware objective dependence is already standard in multiobjective BO | Calibrated joint prediction versus Fréchet marginal-only robustness; demonstrate cases where DRPA hurts |
| Edwards and Schuster, *Ask or Assume?* (Findings EMNLP 2026), [ACL Anthology](https://aclanthology.org/2026.findings-emnlp.15/) | Coding-agent uncertainty-sensitive clarification seeking | **Moderate:** asking for information based on uncertainty is not novel | Explicit action menu and budget matched; separate ambiguous specification from patch-quality estimates |
| **U-CODE: DRPA (this proposal, code-only)** | **Exact restricted 2×2 Fréchet lower/upper HVI; five-resource feasibility; model-conditional ranking stability and STOP** | Mathematical primitives known; real SE-specific benefit untested | Compare independence, fitted joint prediction, robust-marginal model, and uncertainty-free search on independently admitted tasks |

## What could be new *if* experiments support it?

A **repository-agent-specific empirical and algorithmic synthesis**, not first use of Bayesian control or dependence models: *whether an ambiguity set over the joint reliability–security forecast changes the agent's candidate-producing actions under matched five-resource budgets, in ways that improve verified software outcomes compared with strong fitted-joint and uncertainty-free controls*.

## Exploratory factor matrix (NOT nine new registered policies)

| Dimension | Treatment / level 1 | Control / level 2 | Stress or ablation | Measure |
|---|---|---|---|---|
| Dependence assumption | Fréchet maximin DRPA | independence-based EHVI | learned joint/correlated EHVI, fixed true simulated copula | action regret, disagreement, HVI gap |
| Marginal calibration | train-only calibrated | raw prediction | corrupt/shifted marginals, ECE-stratified | Brier, ECE, coverage, under/overconfidence |
| Dependence regimes | weakly identified | high-confidence fitted | anticorrelated, positively correlated, near-independent | decision reversal frequency and effect |
| Budget | five strict caps | same assigned caps | tight/medium/loose; actual spend recorded | tokens/tests/GPU/CPU/wall, paired verified success |
| Action kind | generation / repair frontier | diagnostic evidence separately | ablate code generation and verification gates | distinct candidate count and released correctness |
| Risk/coverage | explicit abstain when no positive lower-net action | nominal positive-EHVI choice | coverage floor and uncertainty shift | ITT success, wrong-release risk, releases |
| Reproducibility | frozen reference point, source lineage, model, seeds | equal opportunities, no gold leakage | full replay versus partial | matched-pair count and attrition |

**Do not silently add an arm to** `configs/confirmatory_sbse_protocol_2026-10-25.json` **or claim that any DRPA variant has run on real code.** The source-only method can serve as an M4 technical appendix or explicitly registered *exploratory ablation* pending independent task admission and a protocol amendment.

## Critical novelty audit questions

1. Does a source-reviewed strong joint multivariate EHVI make the Fréchet bound redundant?
2. Are the frozen marginals good enough to make a robust bound scientifically meaningful, including low-data code-security labels?
3. Does maximin conservatism reduce coverage or success relative to the equal-budget comparator?
4. Are candidate validity and predicted correctness/security correlated? If yes, the present independent validity multiplier invalidates the bound.
5. Does the two-point discretization preserve meaningful real-task decision rankings? What changes with three+ support points or continuous outcomes?
6. Does DRPA confer any benefit after holding candidate samples, task difficulty, model checkpoint, action opportunities and five true resources fixed?
7. Can reviewers verify that the originality, if any, lies in a demonstrated coding-agent decision mechanism rather than repackaged Fréchet bounds?

**Research readout:** mathematical ranking counterexample and source-integrity checks are achievable now; genuine algorithmic novelty and paper-level benefit are unresolved.
