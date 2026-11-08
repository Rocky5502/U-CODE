# U-CODE ten-stage research sprint + truthful heartbeat ledger

**Established 9 November 2026. Ten requested 30-minute *work timeboxes* (total nominal 5 hours), NOT ten running background agents or guaranteed elapsed execution.**

## Scheduling and evidence integrity

The user requested ten autonomous 30-minute stages and ten self-heartbeats. ChatGPT's scheduled tasks support at most one run per hour; **no 30-minute ChatGPT automation has been created**. The table below is an actionable GitHub backlog, not a claim that tasks are executing unattended or that they are finished. Each issue includes a heartbeat template to be filled only after actual work and verified CI. No silent background execution or five-hour compute reservation is promised. Existing unrelated automations are unchanged.

**Actual baseline heartbeats:** 10 status messages have now been posted, one on each issue [#61](https://github.com/Rocky5502/U-CODE/issues/61) through [#70](https://github.com/Rocky5502/U-CODE/issues/70). They record S01 and S02's completed **source-engineering** results, while the remaining eight work items remain **PENDING** or **BLOCKED**. They are not simulated clock-timed runs. This ledger is updated as a source-state snapshot after merge #71; the issues are the live per-stage history.

**Heartbeat rule for every stage:** record the actual date/time, branch and merged PR or pending status; tests actually observed from CI; meaningful changed files; independent spec/oracle/model-security gates still outstanding; and an explicit DONE, PARTIAL or BLOCKED verdict. An open issue, passing synthetic unit test or a scheduled slot never means a real benchmark was completed.

| Planned nominal slot | GitHub issue | Concrete objective | Current status / checkpoint evidence |
|---|---|---|---|
| 00:00–00:30 | [S01 #61](https://github.com/Rocky5502/U-CODE/issues/61) | Leave-one-repository-lineage-out paired intention-to-treat sensitivity | **DONE — engineering only:** [PR #71](https://github.com/Rocky5502/U-CODE/pull/71) merged at `7307ed020b58910a41c29728f7e7f960834f6954`; [post-merge CI](https://github.com/Rocky5502/U-CODE/actions/runs/42512923543) passed 1,651 tests on each Python 3.10 and 3.12; issue #61 heartbeat recorded. Not empirical task evidence |
| 00:30–01:00 | [S02 #62](https://github.com/Rocky5502/U-CODE/issues/62) | Attrition, abstention and wrong-release denominators | **DONE — engineering only:** [PR #73](https://github.com/Rocky5502/U-CODE/pull/73) merged at `e59442b161e7794f932ed368546bfed7f0113484`; [PR CI](https://github.com/Rocky5502/U-CODE/actions/runs/42514548857) and [post-merge CI](https://github.com/Rocky5502/U-CODE/actions/runs/42514726667) passed; 1,670 tests on Python 3.10 and 3.12 in PR checks; 19 new synthetic falsifiers; issue #62 heartbeat recorded. No real model result |
| 01:00–01:30 | [S03 #63](https://github.com/Rocky5502/U-CODE/issues/63) | Five-resource Pareto and budget diagnostics | PENDING / no execution |
| 01:30–02:00 | [S04 #64](https://github.com/Rocky5502/U-CODE/issues/64) | Conditional value-of-information falsification | PENDING / no execution |
| 02:00–02:30 | [S05 #65](https://github.com/Rocky5502/U-CODE/issues/65) | Fidelity of eight baseline policy adapters | PENDING / no execution |
| 02:30–03:00 | [S06 #66](https://github.com/Rocky5502/U-CODE/issues/66) | Dataset lineage contamination checks | PENDING / no execution |
| 03:00–03:30 | [S07 #67](https://github.com/Rocky5502/U-CODE/issues/67) | Go #43 source-era reviewer decision integrity | PENDING / 8 of 8 external gates outstanding |
| 03:30–04:00 | [S08 #68](https://github.com/Rocky5502/U-CODE/issues/68) | PHP #104 spec and rights review preflight | PENDING / 8 of 8 external gates outstanding |
| 04:00–04:30 | [S09 #69](https://github.com/Rocky5502/U-CODE/issues/69) | Six model checkpoint / security provenance audit | PENDING / 0 qualified checkpoints |
| 04:30–05:00 | [S10 #70](https://github.com/Rocky5502/U-CODE/issues/70) | Springer paper and replication consistency | PENDING / 0 real policy comparisons |

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

## Nonnegotiable scientific blockers

- Go #43: source-era normative ambiguities unresolved and no independent reviewer verdict. **8/8 external gates pending.**
- PHP #104: independent source-era specification, rights, hidden oracle, and execution gate unapproved. **8/8 external gates pending.**
- No independently sealed functional oracles, no approved rootless network-off runner or five metered hard caps, no fully qualified six-model checkpoints, no actually faithful all-eight policy experiment and no valid measured ITT treatment effect.
- GitHub repository LaTeX source edits do not sync the live Overleaf account automatically.

## Review and next-stage procedure

After each actual sprint action, update that stage's GitHub issue with a real heartbeat, and if needed update this ledger in a PR. Never mark a stage DONE from merely having source code, a plausible model SHA or untrusted reviewer fields. Progress is measured as implemented and validated engineering, separately from the ten independent scientific milestone exit criteria in [the canonical report](UCODE_PROGRESS_CRITICAL_PATH_2026-11-07.md).
