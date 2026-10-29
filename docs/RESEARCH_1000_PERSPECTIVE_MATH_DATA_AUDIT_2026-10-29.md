# U-CODE — mathematical, data and 1,000-perspective research audit

**Date:** 29 October 2026 · **Evidence class:** independently constructed
first-party, exact-arithmetic unit tests, source-only dataset reconciliation,
and prospective peer-review *scoping*. **NOT 1,000 independently operating
reviewers**, not a proof of journal novelty, not a real coding-agent evaluation,
not an independently sealed oracle and not a completed safety audit.

## A. How 1,000 viewpoints are organized

Run `python -m scripts.export_1000_research_lenses` to build a
machine-readable, deterministic review inventory at
`dist/ucode-review-1000-lenses.json`.

- **20 scientific domains**: SBSE formalization; Bayes/calibration;
  correlated evidence; search algorithms; agent integration; provenance;
  data quality; task admission; software oracles; model selection; GPU
  execution; system security; resource accounting; experimental design;
  metrics/statistics; baselines; multilingual SE; reproducibility;
  literature novelty; Springer publication.
- **10 concrete scientific or engineering risk topics per domain** (200).
- **Five review roles per risk**: theorist, implementation auditor,
  adversarial tester, empirical reviewer, reproducibility editor.
  This yields exactly **20 × 10 × 5 = 1,000 PENDING lenses**.

Every record says `PENDING_NOT_EXECUTED`, with **zero** human reviewer
attestations, completed scientific reviews or experimental claims.
The register structures future research work; it is not evidence of work
that has been performed or an autonomous multi-agent orchestration engine.

## B. Equations checked against independent exact rational enumeration

Source: `src/ucode/reference_math_oracles.py`.
Cross-implementation tests:
`tests/test_independent_rational_mathematics.py`.

### B1. Binary evidence predictive mass and posterior

For joint acceptability (Y \in \{0,1\}), prior
(p=P(Y=1)), sensitivity (s=P(+\mid Y=1)) and specificity
(t=P(-\mid Y=0)), independently recompute

\[
q_+=ps+(1-p)(1-t),\qquad
q_-=p(1-s)+(1-p)t=1-q_+.
\]
\[
p_+=\frac{ps}{q_+}\;(q_+>0),\qquad
p_-=\frac{p(1-s)}{q_-}\;(q_->0).
\]

No posterior is assigned to an impossible observation branch; its
contribution to expected terminal payoff is zero. Exact rational
enumeration checks the Bayes-martingale identity
(q_+p_++q_-p_-=p), with zero-mass terms omitted.
**This requires the assumed conditional likelihoods to be correct.**
No empirical calibration or independence claim is made.

### B2. Hard release gate and signed evidence value

The hypothetical terminal value is

\[
U_0(p)=
\begin{cases}
\max\{pR-(1-p)L,0\}, & 1-p\le \alpha,\\
0, & \text{otherwise},
\end{cases}
\]
where (R,L\ge0) are preregistered release payoff/penalty and
\(\alpha\) a **predicted** failure threshold, not statistical
certification. The one-step diagnostic gain is
\[
\operatorname{EVSI}(a)=q_+U_0(p_+)+q_-U_0(p_-)-U_0(p).
\]

Due to the discontinuous hard gate, signed EVSI can be **negative**.
Do not replace it with a clipped nonnegative quantity or claim ordinary
unconstrained Bayes information monotonicity under this gate.

A separate exact fraction oracle is compared with the floating-point
U-CODE VOI implementation over **375 combinations** of priors,
sensitivities, specificities and risk-gate thresholds, including
degenerate (zero-support) observations. These are synthetic
mathematical cases, not AI agent tasks.

### B3. Exact two-probe counterfactual

With (p=1/2\), (s=t=4/5\), a predicted-failure gate
\(\alpha=1/10\), (R=L=1\), and per-probe scalar price (1/100):

- one positive probe gives (p_+=4/5\), below the release gate;
- two conditionally independent positive probes give
  (p_{++}=16/17\);
- their joint observation probability is (17/50\);
- terminal release payoff for (++\) is (15/17\);
- the continuation policy purchases the second probe only if the first
  is positive: expected price
  (1/100+(1/2)(1/100)=3/200\).

Consequently the exact *conditional* two-step expected net value is
\[
(17/50)(15/17)-3/200
=3/10-3/200=\boxed{57/200=0.285}.
\]

The independent exhaustive two-probe policy enumerator and the BES
finite dynamic program agree on this **invented** case.
If the second observation **duplicates** the first, then its
conditional likelihood is independent of (Y) given the first
signal; purchasing it gives zero additional terminal benefit and
negative net value. The history-conditioned controller correctly
abstains under the same numeric design.

### B4. Partial-identification missingness intervals

For assigned cells (N=s+w+u+n_0\), observed successful releases (s),
wrong releases (w), infrastructure-unknown cells (u) and known
nonrelease failures/abstentions (n_0), enumerate each unknown cell
as successful release / wrong release / no release. The exact
worst/best envelopes are

\[
P(\text{task success})\in[s/N,(s+u)/N],
\quad
P(\text{release})\in[(s+w)/N,(s+w+u)/N].
\]

If (s+w+u>0), possible conditional wrong-release risk is in

\[
\left[\frac{w}{s+w+u},\;
      \frac{w+u}{s+w+u}\right].
\]

If there are **no known or possible releases** it is *undefined*.
The exact oracle exhaustively checks **191** small integer tuples
(0–3 successes, 0–3 wrong, 0–3 unknown, 0–2 known nonreleases,
excluding the empty assignment) against these closed forms.
These are sharp logical missingness envelopes, **not confidence
intervals or calibrated statistical risk guarantees**.

### B5. What these checks do **not** prove

- Correct transition kernels on real software: **not established**.
- Probability calibration on held-out repository families: **not established**.
- Independence of two real diagnostics: **not established**.
- Optimality of a general coding-agent POMDP or search in continuous
  belief spaces: **not established**.
- Correct independent functionality of any real repair patch: **0 tasks**.
- Physical hardware metering, CPU/GPU safety, or prompt isolation: **unverified**.
- A model/policy effectiveness advantage: **no observations**.

Formal bounded-tree optimality is valid only conditional on a fixed
finite state/action/observation transition model and the exact budget,
candidate, terminal utility and action-reuse assumptions listed in
[the BES method](BES_ALGORITHM_METHOD_AND_FALSIFIERS_2026-10-24.md).

## C. Exact dataset source/grain reconciliation

Run `python -m scripts.audit_dataset_cohort_crosswalk`.

Independently join each of **120** original discovery rows to the
120-row frozen curated discovery frame by ID and compare
repository, PR URL and *search-language stratum*; require 12 strata ×
10 records and all tasks remain `NOT_ADMITTED`, oracle
`NOT_VERIFIED`, split `NOT_SPLIT`.

The separate source registries contain **13 newer prospective external
dataset leads** and **10 legacy leads**. The crosswalk refuses to
relabel any of these as downloaded, licensed or executed.
The frozen screening summary records **119** retrieved PR metadata,
**62** production-source-path leads and **0** independently
eligible executable tasks. Identity equality, schema, missing
IDs, catalog duplicates, HTTP URLs and status self-promotion are
tested adversarially.

This is *static source consistency* against the frozen summary, not
a live GitHub/API provenance re-attestation or independent license
review. The 12 discovery-language strata do not imply 12 true
changed-code languages or 12 tested language ecosystems.

## D. Actual manuscript source issue discovered and repaired

The previous `paper/overleaf/main.tex` source contained doubled
backslashes before two `cite` and two `emph` commands in the
guided-search and SearchSYS related-work passages. In TeX,
`\\cite` is **not** the same as `\cite`: it can typeset
an unintended line break and plain text instead of the command.
The source was repaired and the Springer source auditor was
strengthened to reject future doubled command prefixes.
**This is source-level remediation, not a claim that the official
Springer template has been compiled or visually approved.**

## E. Next scientific priority

Before obtaining any positive real RQ evidence:

1. Independent task-era specification and rights adjudication for PHP
   #104 (or a better sourced task); reject/relabel reconstructed tasks.
2. An independent sealed evaluator and version-pinned rootless,
   offline trusted code-execution runner with five independently
   measured/enforced resources.
3. Frozen model weights/tokenizer/chat-template/runtimes after terms
   approval; record actual VRAM/latency.
4. Training-only calibration and conditional diagnostic likelihood
   fitting with lineage-held-out evaluation.
5. Matched, faithful baseline comparisons, ITT accounting, negative
   results and group-cluster uncertainty intervals.

**Use** `python -m unittest discover -s tests -v`,
`python -m scripts.audit_overleaf_sources`,
`python -m scripts.audit_dataset_cohort_crosswalk`, and
`python -m scripts.export_1000_research_lenses` to reproduce
first-party offline checks. No third-party code/model execution occurs.
