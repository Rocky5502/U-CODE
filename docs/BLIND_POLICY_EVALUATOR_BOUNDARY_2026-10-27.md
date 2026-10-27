# Evaluator-blind policy trace: engineering boundary (27 October 2026)

**Status:** offline reference implementation only; no approved executable repository
tasks, no real LLM inference and no independent oracle run.

## New executable interfaces

- `src/ucode/task_view_boundary.py`: immutable `AgentTaskView`, exact
  four-field projection (`repository`, pinned `base_sha`,
  `prefixed_spec`, `spec_sha256`). Metadata rejection does NOT prove the
  text was available at the pre-fix timestamp or that it is free of spoilers.
  Never pass post-fix PR dossiers or reviewer packets through this interface.
- `src/ucode/blind_policy_trace.py`: `run_blind_policy` accepts that view,
  a hard five-vector budget, a policy callback and one **policy-visible**
  tool adapter. **It does not accept a hidden evaluator callback.**
  The policy observes only the task view, candidate patch, prior public
  steps and remaining budget. Evaluator-only gold verdicts remain outside
  the trace API and must be obtained only after the session ends.
- Each nonterminal action reserves an explicit five-vector **maximum**
  before tool dispatch. The typed `PublicToolReceipt` records reported
  actual usage; usage beyond the maximum, wrong action types or adapter
  exceptions halt without release and mark accounting unverified. The
  reservation is conservatively retained when accounting fails; it is
  **not** evidence of measured consumption.
- Release returns `RELEASED_PENDING_INDEPENDENT_EVALUATION` and an
  immutable trace, never a correctness label. Abstention is explicit.
  An invalid release without a candidate is not counted as success.

## Why this matters for RQ3

A held-out full-task evaluator must never be an action-search tool.
Otherwise the experimental policy can optimize against oracle leakage
instead of learning where to spend its diagnostic budget. The current
legacy `src/ucode/agent.py` remains a scalar-budget **mock/reference**
whose provided verifier feedback can reach subsequent policy steps. It
must NOT be attached to a held-out oracle or deployed as the confirmatory
runner. The blind trace is a more appropriate foundation for future
policy adapters, not a completed agent.

## Required external controls before real trials

1. Independently attested pre-fix issue/spec snapshots, task rights, fork
   lineage and SHA-pinned source; task admission remains **zero**.
2. Trusted separation of public diagnostic feedback versus sealed private
   evaluator tests and verdicts. A structured schema cannot certify that
   free-text feedback contains no hidden-oracle information.
3. A rootless, network-disabled, credential-free, disposable execution
   sandbox. The Python policy does not directly execute foreign code.
4. Trusted enforcement and measurement of tokens, test calls, GPU seconds,
   CPU seconds and wall seconds **during** execution. A caller-supplied
   Python `ResourceVector` is NOT a metering attestation and a tool may
   exceed its declared upper bound before returning.
5. Frozen checkpoint, seed, task-family split, predictor/calibration model,
   complete eight-policy comparator implementations, and preregistered
   matched budgets. This reference skeleton does not implement them.
6. After the policy terminates, a separate sealed evaluator records
   correctness with every assigned denominator and attrition reason,
   including no-release, measurement failure and infrastructure loss.

## Adversarial offline tests

`tests/test_task_view_boundary.py` rejects extra PR-head/oracle fields,
modified task text, invalid identities and forged dossier input.
`tests/test_blind_policy_trace.py` exercises evaluator-free traces,
schema rejection of hidden-verdict fields, each of the five cap
dimensions, receipt overrun, thrown tool exceptions, wrong action
identities, invalid release and reproducible mock traces.

These are tests of interface invariants, NOT empirical verification of
third-party repository repairs or real five-dimensional metering.
