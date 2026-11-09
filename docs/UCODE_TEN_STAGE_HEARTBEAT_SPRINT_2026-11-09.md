# U-CODE ten-stage research sprint + truthful heartbeat ledger

**Established 9 November 2026. Ten requested 30-minute *work timeboxes* (total nominal 5 hours), NOT ten running background agents or guaranteed elapsed execution.**

## Scheduling and evidence integrity

The user requested ten autonomous 30-minute stages and ten self-heartbeats. ChatGPT's scheduled tasks support at most one run per hour; **no 30-minute ChatGPT automation has been created**. The table below is an actionable GitHub backlog, not a claim that tasks are executing unattended or that they are finished. Each issue includes a heartbeat template to be filled only after actual work and verified CI. No silent background execution or five-hour compute reservation is promised. Existing unrelated automations are unchanged.

**Actual baseline heartbeats:** 10 status messages have now been posted, one on each issue [#61](https://github.com/Rocky5502/U-CODE/issues/61) through [#70](https://github.com/Rocky5502/U-CODE/issues/70). All ten tickets now have evidence-backed source-engineering checkpoints (S01–S04 single-stage implementations; S05–S10 jointly checked in PR #79). **External scientific approval is still blocked** for S05 comparator fidelity, S06 lineage split, S07 Go #43, S08 PHP #104, S09 six-model qualification and S10 empirical results. They are not simulated clock-timed runs. This ledger is updated as a source-state snapshot after merge #79; the issues are the live per-stage history.

**Heartbeat rule for every stage:** record the actual date/time, branch and merged PR or pending status; tests actually observed from CI; meaningful changed files; independent spec/oracle/model-security gates still outstanding; and an explicit DONE, PARTIAL or BLOCKED verdict. An open issue, passing synthetic unit test or a scheduled slot never means a real benchmark was completed.

| Planned nominal slot | GitHub issue | Concrete objective | Current status / checkpoint evidence |
|---|---|---|---|
| 00:00–00:30 | [S01 #61](https://github.com/Rocky5502/U-CODE/issues/61) | Leave-one-repository-lineage-out paired intention-to-treat sensitivity | **DONE — engineering only:** [PR #71](https://github.com/Rocky5502/U-CODE/pull/71) merged at `7307ed020b58910a41c29728f7e7f960834f6954`; [post-merge CI](https://github.com/Rocky5502/U-CODE/actions/runs/42512923543) passed 1,651 tests on each Python 3.10 and 3.12; issue #61 heartbeat recorded. Not empirical task evidence |
| 00:30–01:00 | [S02 #62](https://github.com/Rocky5502/U-CODE/issues/62) | Attrition, abstention and wrong-release denominators | **DONE — engineering only:** [PR #73](https://github.com/Rocky5502/U-CODE/pull/73) merged at `e59442b161e7794f932ed368546bfed7f0113484`; [PR CI](https://github.com/Rocky5502/U-CODE/actions/runs/42514548857) and [post-merge CI](https://github.com/Rocky5502/U-CODE/actions/runs/42514726667) passed; 1,670 tests on Python 3.10 and 3.12 in PR checks; 19 new synthetic falsifiers; issue #62 heartbeat recorded. No real model result |
| 01:00–01:30 | [S03 #63](https://github.com/Rocky5502/U-CODE/issues/63) | Five-resource Pareto and budget diagnostics | **DONE — engineering only:** [PR #75](https://github.com/Rocky5502/U-CODE/pull/75) merged at `be49f91601e066b5deba933ede100326b98d6f06`; [PR CI](https://github.com/Rocky5502/U-CODE/actions/runs/42548644468) and [post-merge CI](https://github.com/Rocky5502/U-CODE/actions/runs/42548745600) passed 1,697 tests plus 22 additional checks on Python 3.10 and 3.12; 27 synthetic Pareto falsifiers and issue #63 heartbeat. No real model or hardware evidence |
| 01:30–02:00 | [S04 #64](https://github.com/Rocky5502/U-CODE/issues/64) | Conditional value-of-information falsification | **DONE — engineering only:** [PR #77](https://github.com/Rocky5502/U-CODE/pull/77) merged at `c002ed67fcc4c71e5f13433b1897100f35508042`; [PR CI](https://github.com/Rocky5502/U-CODE/actions/runs/42550432553) and [postmerge CI](https://github.com/Rocky5502/U-CODE/actions/runs/42550572873) passed on Python 3.10 and 3.12; 1,719 offline tests + 22 additional checks per version; 22 synthetic S04 falsifiers; [issue #64 heartbeat](https://github.com/Rocky5502/U-CODE/issues/64) recorded. No real model or oracle evidence |
| 02:00–02:30 | [S05 #65](https://github.com/Rocky5502/U-CODE/issues/65) | Fidelity of eight baseline policy adapters | **SOURCE AUDIT DONE** ([PR #79](https://github.com/Rocky5502/U-CODE/pull/79)): aliased handler factories exposed and eight fidelity gaps enumerated. **BLOCKED** on independent algorithm-method review; 0/8 fidelity verified |
| 02:30–03:00 | [S06 #66](https://github.com/Rocky5502/U-CODE/issues/66) | Dataset lineage contamination checks | **SOURCE AUDIT DONE** ([PR #79](https://github.com/Rocky5502/U-CODE/pull/79)): 120-PR graph semantic verifier and 10 self-rehash/tampering tests. **BLOCKED** on independently verified lineage split; no task duplicates certified |
| 03:00–03:30 | [S07 #67](https://github.com/Rocky5502/U-CODE/issues/67) | Go #43 source-era reviewer decision integrity | **PUBLIC HANDOFF AUDITED** ([PR #79](https://github.com/Rocky5502/U-CODE/pull/79)): six unresolved normative questions, 12 review-only cases, no gold. **BLOCKED** on independent domain review; 8/8 external gates pending |
| 03:30–04:00 | [S08 #68](https://github.com/Rocky5502/U-CODE/issues/68) | PHP #104 spec and rights review preflight | **PUBLIC HANDOFF AUDITED** ([PR #79](https://github.com/Rocky5502/U-CODE/pull/79)): original issue text, rights and 10 no-gold case families crosschecked. **BLOCKED** on independent review; 8/8 external gates pending |
| 04:00–04:30 | [S09 #69](https://github.com/Rocky5502/U-CODE/issues/69) | Six model checkpoint / security provenance audit | **PUBLIC METADATA AUDITED** ([PR #79](https://github.com/Rocky5502/U-CODE/pull/79)): six unchanged IDs, no signed weights/licenses/VRAM/runtimes. **BLOCKED** on authenticated qualification; 0/6 runnable |
| 04:30–05:00 | [S10 #70](https://github.com/Rocky5502/U-CODE/issues/70) | Springer paper and replication consistency | **GITHUB SOURCE AUDITED** ([PR #79](https://github.com/Rocky5502/U-CODE/pull/79)): method markers, N/A primary effect, no verified live Overleaf/PDF. **BLOCKED** on independent real experiment and publication-ready results |

These are **nominal planned durations, not estimates that a stage can be finished in exactly 30 minutes**. Dependency failures should produce a truthful BLOCKED heartbeat, not a fabricated completion.

## Stage S01: paired assignment-level leave-one-lineage-out influence

The new evaluator-only [source module](../src/ucode/lineage_influence.py) and [synthetic adversarial tests](../tests/test_lineage_influence.py) quantify whether assignment-level success differences are dominated by one repository/fork lineage. A claim of generalization across repositories is unconvincing if the positive effect disappears or reverses on removing just one lineage.

For (N) fully matched task/model/seed/budget policy pairs with independent **evaluator-only** verified-success indicators, write `d_i = y_i(treatment) - y_i(control)`. For each declared repository/fork group `g` with `N_g` assigned pairs and `D_g = sum_{i in g} d_i`:

```text
overall_delta       = sum_i d_i / N
omitted_group_delta = (sum_i d_i - D_g) / (N - N_g), if N - N_g > 0
absolute_influence  = abs(omitted_group_delta - overall_delta)
```

The report includes every declared lineage, its omitted assignment count, sensitivity of the pooled effect, strict sign reversals and the largest declared family share. An omission that leaves **zero** pairs produces N/A, never a numeric zero. The analysis is **descriptive only**. It does not produce a valid population CI, randomization p-value or proof that the claimed lineages are truly independent. Repeated seeds and multiple models remain in the assignment-level denominator, and all observations in the same lineage are withheld together.

```bash
python -m unittest discover -s tests -p 'test_lineage_influence.py' -v
python -m unittest discover -s tests -v
```

The eight-policy six-model *real* factorial design remains prospective. This is a first-party structural diagnostic on synthetic regressions and could be used later **only after** a separate sealed evaluator and independently admitted tasks produce authentic outcomes.

## Stage S02: exact postterminal missingness and wrong-release denominators

[Issue #62](https://github.com/Rocky5502/U-CODE/issues/62) has a verified engineering heartbeat. Merged [PR #73](https://github.com/Rocky5502/U-CODE/pull/73) adds [paired missingness sign sensitivity](../src/ucode/attrition_sign_sensitivity.py), [19 adversarial first-party tests](../tests/test_attrition_sign_sensitivity.py), and a [source-only methods note](S02_ATTRITION_SIGN_FALSIFIERS_2026-11-09.md). The code checks that the original assignment denominator is preserved, re-derives sharp treatment-minus-control worst/best outcomes from *integer* counts of known success and unknown infrastructure failures, and reports whether negative, zero or positive effects remain possible. Exhaustive fictional small cases test the conditional wrong-release risk denominator, including genuinely undefined zero-release cases.

**Scope:** mathematical/first-party source engineering, not a measured effect, independent evaluator attestation, approved model, real code-repair task, or actual hardware record. The planned six-model/eight-policy factorial benchmark is still blocked. The ten nominal 30-minute timeboxes remain **planning labels only**; these recorded heartbeats are evidence-backed updates rather than uninterrupted hourly or half-hourly agent execution.

## Stage S03: fixed-cap matched quality × five-resource Pareto diagnostics

[Issue #63](https://github.com/Rocky5502/U-CODE/issues/63) now has a verified engineering heartbeat. Merged [PR #75](https://github.com/Rocky5502/U-CODE/pull/75) adds [postterminal matched six-objective Pareto validation](../src/ucode/matched_pareto_audit.py), [27 synthetic adversarial cases](../tests/test_matched_pareto_audit.py), and a [precise method/limitations report](S03_MATCHED_PARETO_HYPERVOLUME_2026-11-09.md). This **is distinct** from the existing pre-outcome two-objective DRPA acquisition controller. The report preserves the original task × seed assignment denominator and separately enforces five hard budget caps per frozen model and budget. The bounded coordinate-sweep six-objective hypervolume uses the union (not sum) of origin-anchored boxes; independent inclusion–exclusion checks it on synthetic tradeoffs and ties. Missing evaluator verdicts and any nonterminal failed run prevent positive frontier claims. No system-independent oracle, model, rights, physical hardware metering or result was verified by this work.

**CI evidence:** [premerge](https://github.com/Rocky5502/U-CODE/actions/runs/42548644468) and [postmerge](https://github.com/Rocky5502/U-CODE/actions/runs/42548745600) both passed Python 3.10 and 3.12 tests (1,697 offline first-party unit tests plus a separate 22-test batch on each). As of this S04 ledger, **four of ten engineering stages** have verified changes, but **none** of the ten independent empirical milestone exits is certified. The nominal 30-minute slots are planning labels, not proof of unattended execution.

## Stage S04: falsifying contradictory two-order conditional likelihoods

[Issue #64](https://github.com/Rocky5502/U-CODE/issues/64) now has a verified source-engineering heartbeat. Merged [PR #77](https://github.com/Rocky5502/U-CODE/pull/77) adds a [bounded conditional-kernel order coherence audit](../src/ucode/conditional_kernel_coherence.py), [22 synthetic falsifiers](../tests/test_conditional_kernel_coherence_s04.py), an opt-in `require_order_coherence=True` planner preflight, and [scope/limitations documentation](S04_CONDITIONAL_ORDER_COHERENCE_FALSIFICATION_2026-11-09.md). Within a fixed candidate and latent correctness class, a necessary joint-model condition is that the probability of the same two visible diagnostic observations agree when computed from either admissible acquisition order. Sparse alternative histories are **incomplete**, not assumed coherent; contradicted event-class probabilities are fail-closed and may be inspected as mathematical counterexamples. Reserved terminal action identifiers and terminal-only once-only cost validation were also hardened.

**Evidence:** [pre-merge CI](https://github.com/Rocky5502/U-CODE/actions/runs/42550432553) and [post-merge CI](https://github.com/Rocky5502/U-CODE/actions/runs/42550572873) both succeeded for Python 3.10 and 3.12; **1,719 first-party offline tests plus 22 separate checks** per version. This is a bounded *necessary local* probability consistency check, not proof of global joint-model coherence, calibration, validated training rights, independent hidden oracles or actual coding-agent improvement. The strict planner option remains **opt-in**. GitHub LaTeX source was updated, not independently confirmed synced to live Overleaf. Four of ten *engineering stages* now have verified changes; **zero real confirmatory trial exits are independently certified**, and the nominal 30-minute slots were never unattended scheduled runs.

## S05–S10 combined engineering audit — actual checkpoint (9 November 2026)

All six remaining issue-specific [heartbeats #65–#70](https://github.com/Rocky5502/U-CODE/issues) now reference one independently inspectable GitHub implementation: [PR #79](https://github.com/Rocky5502/U-CODE/pull/79), squash merged as `48d92c43bb58db5495f20bd1b41bac03c40af94e`. [PR CI](https://github.com/Rocky5502/U-CODE/actions/runs/42556870051) and [postmerge CI](https://github.com/Rocky5502/U-CODE/actions/runs/42557022267) both passed **1,750 first-party offline tests plus a separate 22-test batch on Python 3.10 and on 3.12**. This is a unified source-engineering checkpoint, **not six separate 30-minute unattended agent runs**.

The [S05–S10 public audit and handoff report](S05_S10_FIDELITY_LINEAGE_ADMISSION_MODEL_MANUSCRIPT_AUDIT_2026-11-09.md) details S05 callback alias detection without method-fidelity promotion; S06 potential-lineage CSV semantic verification, including forged-but-self-rehashed metadata; S07 six unresolved Go #43 normative questions and twelve public-only cases; S08 ten PHP #104 public no-gold cases and unresolved source rights; S09 the six public model card metadata gaps; and S10 source-versus-empirical manuscript claims.

The [offline six-stage CLI](../scripts/audit_remaining_sprint.py) crosschecks all these against the unchanged registered six-model/eight-policy design, the original pilot preflight and the canonical critical path. Its strict `--require-real-ready` mode **must exit 2**; the first-party CI checks this and publishes only a public metadata receipt. Every model access, reviewer approval, hidden evaluator, live Overleaf synchronization or real task effect is **unverified**. All **ten sprint issue scopes have now been addressed with source-level evidence**, but this does **not** satisfy any of the **ten independently validated scientific milestone exits**. External blockers are not converted into completed tasks or a percentage of actual research performed.

## Nonnegotiable scientific blockers

- Go #43: source-era normative ambiguities unresolved and no independent reviewer verdict. **8/8 external gates pending.**
- PHP #104: independent source-era specification, rights, hidden oracle, and execution gate unapproved. **8/8 external gates pending.**
- No independently sealed functional oracles, no approved rootless network-off runner or five metered hard caps, no fully qualified six-model checkpoints, no actually faithful all-eight policy experiment and no valid measured ITT treatment effect.
- GitHub repository LaTeX source edits do not sync the live Overleaf account automatically.

## Review and next-stage procedure

After each actual sprint action, update that stage's GitHub issue with a real heartbeat, and if needed update this ledger in a PR. Never mark a stage DONE from merely having source code, a plausible model SHA or untrusted reviewer fields. Progress is measured as implemented and validated engineering, separately from the ten independent scientific milestone exit criteria in [the canonical report](UCODE_PROGRESS_CRITICAL_PATH_2026-11-07.md).
