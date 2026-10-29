# U-CODE — history-conditional BES meets matched public replay (29 October 2026)

**Stage: offline synthetic mechanism test, NOT an empirical LLM coding-agent study.**

## New working integration

`src/ucode/conditional_bes_public_replay.py` now wires an existing
finite-horizon `plan_conditional` controller into the exact candidate-bound
`ActionBoundBook` and `SharedSession` mechanism used for other synthetic
reference policies. Unlike predetermined traces, after every visible public
diagnostic the controller actually replans from its frozen likelihood model
and the remaining five-dimensional resource vector. Actions are selected
from the current shared public action-ID and candidate-target menu. A
missing public response or conditional likelihood fails closed.

The reference generates **at most one artificial candidate** and then
selects from diagnostic actions (test, static analysis, retrieval).
It cannot yet optimize repair, another generate call, multiple candidates,
joint correlated patch correctness, live tokens, executable tests or model
inference. Therefore the registered `ucode_conditional_bes` identifier
is used for a **strictly scoped synthetic implementation**, NOT a faithful
full treatment policy or evidence of experimental completion.

## Reproducible falsifier

Run:

```bash
python -m scripts.smoke_conditional_bes_public_replay
python -m scripts.smoke_uncertainty_only_reference
python -m unittest discover -s tests -v
```

For an artificially generated candidate with a stipulated pre-outcome
acceptability prior `0.5`, public test `a` and static-analysis probe
`b` have independent conditional likelihoods `P(+|Y=1)=0.8` and
`P(+|Y=0)=0.2` in this hypothetical scenario. The release threshold
is `0.9`. With `0.01` predeclared cost per probe, the two-step
conditional planner can purchase `a`, see positive evidence, purchase
`b`, see positive evidence, and release the synthetic candidate based
on its model posterior `16/17 ≈ 0.941`.

The separate one-test `uncertainty_only` reference has **identical
catalogue, budget, candidate and public response book**, but by its
own frozen single-test decision rule it abstains after one positive
test (posterior `0.8`). This is an intentionally constructed **action
decision difference**, NOT a real pass/fail test or verified advantage.
Neither release is a correctness verdict.

A redundancy counterexample swaps in a history-conditioned model under
which the second probe is informationally redundant. The planner then
abstains rather than buying a pointless test. Both cases demonstrate
mechanism testability, not the accuracy of any fitted diagnostic model.

## Research-integrity constraints

- All source task IDs must begin `SYNTHETIC_`; no PHP/Go source runs.
- Hypothetical confidence cards, conditional likelihood rows and price
  schedules are immutable typed inputs and never read hidden evaluator
  labels; training/validation/testing splits are not established.
- Shared action IDs are single-use and candidate-bound; nominal
  reservations and public-receipt costs are checked by the shared ledger,
  but neither is authenticated OS/hardware metering.
- A missing, impossible or contradictory conditional history fails
  closed. There is **no independence fallback**.
- Source-level test status and stop decisions are not statistical
  reliability guarantees.
- The implementation is deliberately **not** real correlated
  multi-candidate BES, generation-versus-evidence allocation, an eight-policy
  fidelity test, or a real success/coverage/risk comparison.

## Next mandatory gates

1. Independently admit one original source-era or separately designed
   prospective task with rights, sealed functional oracle and an isolated
   reproducible runner.
2. Fit and freeze *real* pre-outcome risk and history-dependent diagnostic
   likelihoods on independently separated training tasks.
3. Extend this diagnostic-only controller to choose among feasible
   generate/retrieve/test/static/repair/abstain with the same action-ID
   receipts as the no-uncertainty comparator.
4. Validate model checkpoint identity, tool permissions and independently
   metered five-resource traces, with evaluator joins **only after** release.
5. Run a preregistered matched-task evaluation that can overturn the
   proposed effectiveness hypothesis.

No manuscript Results table should contain the synthetic trace as an
empirical task success.
