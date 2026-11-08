"""Synthetic exhaustive falsifiers for S02 postterminal missingness bounds.

Every task and evaluator label below is fabricated for first-party CI;
there is no real model inference, repository execution, reviewer attestation,
meter authentication, signed oracle or empirical U-CODE result.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from fractions import Fraction
from itertools import product
import json
import unittest

from ucode.attrition_sign_sensitivity import audit_attrition_sign_sensitivity
from ucode.experiment_contract import EvaluatorVerdict, FrozenStudy, PolicyRunReceipt
from ucode.postterminal_accounting import _arm, postterminal_contrast
from ucode.vector_policy import ResourceVector as RV


T, C = "ucode_conditional_bes", "no_uncertainty_search"
STATES = {
    "correct": ("release", True),
    "wrong": ("release", False),
    "abstain": ("abstain", None),
    "timeout": ("timeout", None),
    "safety": ("safety_block", None),
    "infra": ("infrastructure_failure", None),
}
CAP = RV(tokens=500, test_calls=10, gpu_seconds=10, cpu_seconds=10,
         wall_seconds=20)
USED = RV(tokens=20, test_calls=1, gpu_seconds=.2, cpu_seconds=2,
          wall_seconds=3)


def make_fixture(rows, *, extra_policy=None):
    """Each row is (treatment_state, control_state); optional extra arm.

    Synthetic patch IDs differ by policy, so incompatible oracle verdicts
    can be represented without contradicting the same task/patch identity.
    """
    if not rows:
        raise ValueError("synthetic study must contain assigned tasks")
    policies = (T, C) if extra_policy is None else (T, C, "extra_policy")
    study = FrozenStudy(
        tuple((f"fake-task-{i}", f"fake-fork-{i}") for i in range(len(rows))),
        ("fake-model",), policies, (17,), (("pilot", CAP),)
    )
    receipts, verdicts = [], []
    for i, values in enumerate(rows):
        statuses = values if extra_policy is None else values + (extra_policy,)
        for j, (policy, state) in enumerate(zip(policies, statuses)):
            termination, truth = STATES[state]
            digest = format(1 + i * 3 + j, "064x")
            receipt = PolicyRunReceipt(
                task_id=f"fake-task-{i}",
                lineage_group=f"fake-fork-{i}",
                model_id="fake-model",
                policy=policy,
                seed=17,
                budget_id="pilot",
                pre_fix_base_sha="a" * 40,
                model_checkpoint_sha40="b" * 40,
                tool_access_sha256="c" * 64,
                environment_image_sha256="d" * 64,
                consumed=USED,
                termination=termination,
                patch_sha256=digest if termination == "release" else None,
                visible_policy_log_sha256="e" * 64,
            )
            receipts.append(receipt)
            if termination == "release":
                verdicts.append(EvaluatorVerdict(
                    task_id=f"fake-task-{i}",
                    model_id="fake-model",
                    policy=policy,
                    seed=17,
                    budget_id="pilot",
                    patch_sha256=digest,
                    oracle_artifact_sha256="f" * 64,
                    oracle_passed=truth,
                    evaluator_log_sha256="9" * 64,
                ))
    return study, tuple(receipts), tuple(verdicts)


def sign_audit(rows, **kwargs):
    study, receipts, verdicts = make_fixture(rows, **kwargs)
    return audit_attrition_sign_sensitivity(study, receipts, verdicts, T, C)


def exact_conditional_risk(r, w, u):
    """Independent brute force over no-release / correct / wrong completions.

    Undefined cases where nobody released anything are excluded from this
    *conditional-on-at-least-one-release* partial-identification range.
    """
    values = []
    for unknown in product((None, False, True), repeat=u):
        unknown_releases = sum(v is not None for v in unknown)
        denominator = r + unknown_releases
        if denominator:
            unknown_wrong = sum(v is False for v in unknown)
            values.append(Fraction(w + unknown_wrong, denominator))
    return ((float(min(values)), float(max(values)))
            if values else None)


class AttritionSignSensitivityTests(unittest.TestCase):
    def test_both_arm_missingness_all_three_effect_signs(self):
        x = sign_audit([
            ("correct", "infra"),
            ("infra", "wrong"),
            ("timeout", "safety"),
            ("wrong", "correct"),
        ])
        self.assertEqual(x.assigned_matched_pairs, 4)
        self.assertEqual((x.treatment_infrastructure_missing,
                          x.control_infrastructure_missing), (1, 1))
        self.assertEqual((x.treatment_known_verified_successes,
                          x.control_known_verified_successes), (1, 1))
        self.assertEqual((x.lower_difference_numerator,
                          x.upper_difference_numerator), (-1, 1))
        self.assertEqual((x.lower_effect, x.upper_effect), (-.25, .25))
        self.assertEqual(x.interval_width, .5)
        self.assertEqual(x.attainable_effect_signs,
                         ("NEGATIVE", "ZERO", "POSITIVE"))
        self.assertFalse(x.sign_robust_to_all_binary_completions)
        self.assertFalse(x.point_identified_under_binary_missingness)
        self.assertEqual(x.treatment_observed_wrong_release_risk, .5)
        self.assertEqual(x.control_observed_wrong_release_risk, .5)
        self.assertEqual(x.treatment_potential_wrong_release_risk_bounds,
                         (1/3, 2/3))
        self.assertEqual(x.control_potential_wrong_release_risk_bounds,
                         (1/3, 2/3))

    def test_treatment_only_unknown_can_still_force_positive(self):
        x = sign_audit([("infra", "abstain"), ("correct", "abstain")])
        self.assertEqual((x.lower_effect, x.upper_effect), (.5, 1.0))
        self.assertEqual(x.attainable_effect_signs, ("POSITIVE",))
        self.assertTrue(x.sign_robust_to_all_binary_completions)
        self.assertFalse(x.point_identified_under_binary_missingness)

    def test_control_only_unknown_can_still_force_negative(self):
        x = sign_audit([("abstain", "infra"), ("abstain", "correct")])
        self.assertEqual((x.lower_effect, x.upper_effect), (-1., -.5))
        self.assertEqual(x.attainable_effect_signs, ("NEGATIVE",))
        self.assertTrue(x.sign_robust_to_all_binary_completions)

    def test_single_treatment_unknown_allows_zero_or_positive(self):
        x = sign_audit([("infra", "abstain")])
        self.assertEqual(x.attainable_effect_signs, ("ZERO", "POSITIVE"))
        self.assertEqual((x.lower_effect, x.upper_effect), (0., 1.))
        self.assertFalse(x.sign_robust_to_all_binary_completions)
        self.assertEqual(x.interval_width, 1.)

    def test_single_control_unknown_allows_negative_or_zero(self):
        x = sign_audit([("abstain", "infra")])
        self.assertEqual(x.attainable_effect_signs, ("NEGATIVE", "ZERO"))
        self.assertEqual((x.lower_effect, x.upper_effect), (-1., 0.))

    def test_both_arm_unknown_per_pair_spans_full_effect(self):
        x = sign_audit([("infra", "infra"), ("infra", "infra")])
        self.assertEqual(x.total_unknown_binary_outcomes, 4)
        self.assertEqual(x.interval_width, 2.0)
        self.assertEqual((x.lower_effect, x.upper_effect), (-1., 1.))
        self.assertIsNone(x.treatment_observed_wrong_release_risk)
        self.assertIsNone(x.control_observed_wrong_release_risk)
        self.assertEqual(x.treatment_potential_wrong_release_risk_bounds,
                         (0., 1.))
        self.assertEqual(x.control_potential_wrong_release_risk_bounds,
                         (0., 1.))

    def test_timeout_and_safety_known_zero_but_bootstrap_suppressed(self):
        x = sign_audit([("timeout", "safety"), ("abstain", "abstain")])
        self.assertEqual(x.total_unknown_binary_outcomes, 0)
        self.assertEqual(x.attainable_effect_signs, ("ZERO",))
        self.assertTrue(x.point_identified_under_binary_missingness)
        self.assertTrue(x.suppressed_bootstrap_despite_identified_itt)
        self.assertEqual((x.lower_effect, x.upper_effect), (0., 0.))
        self.assertIsNone(x.treatment_observed_wrong_release_risk)

    def test_all_abstain_has_risk_undefined_and_no_suppression(self):
        x = sign_audit([("abstain", "abstain")])
        self.assertTrue(x.point_identified_under_binary_missingness)
        self.assertFalse(x.suppressed_bootstrap_despite_identified_itt)
        self.assertEqual(x.attainable_effect_signs, ("ZERO",))
        self.assertIsNone(x.treatment_observed_wrong_release_risk)
        self.assertIsNone(x.treatment_potential_wrong_release_risk_bounds)
        self.assertIsNone(x.control_potential_wrong_release_risk_bounds)

    def test_unrelated_third_policy_failure_does_not_enter_primary_bounds(self):
        x = sign_audit([("correct", "abstain"), ("wrong", "wrong")],
                       extra_policy="infra")
        self.assertEqual(x.assigned_matched_pairs, 2)
        self.assertEqual(x.total_unknown_binary_outcomes, 0)
        self.assertEqual(x.attainable_effect_signs, ("POSITIVE",))
        self.assertTrue(x.point_identified_under_binary_missingness)
        # Canonical source-only contract conservatively suppresses point
        # bootstrap if any of the FULL eight-policy matrix has attrition.
        self.assertTrue(x.suppressed_bootstrap_despite_identified_itt)

    def test_source_order_invariance(self):
        rows = [("wrong", "correct"), ("correct", "infra"),
                ("infra", "wrong"), ("abstain", "safety")]
        a = sign_audit(rows)
        b = sign_audit(list(reversed(rows)))
        # Tasks are synthetic and renamed, but the aggregate diagnostic
        # must not change with the order of identical outcome categories.
        self.assertEqual(asdict(a), asdict(b))

    def test_wrong_policy_or_same_arm_denied(self):
        study, records, gold = make_fixture([("abstain", "abstain")])
        for t, c in ((T, T), (T, "oracle-hack")):
            with self.subTest(t=t, c=c), self.assertRaisesRegex(
                    ValueError, "preregistered"):
                audit_attrition_sign_sensitivity(study, records, gold, t, c)

    def test_missing_pair_cannot_shrink_denominator(self):
        study, records, gold = make_fixture([("correct", "infra")])
        with self.assertRaisesRegex(ValueError, "incomplete"):
            audit_attrition_sign_sensitivity(study, records[:-1], gold, T, C)

    def test_missing_release_oracle_cannot_be_scored_correct(self):
        study, records, gold = make_fixture([("correct", "wrong")])
        with self.assertRaisesRegex(ValueError, "lacks"):
            audit_attrition_sign_sensitivity(study, records, gold[:-1], T, C)

    def test_forged_nonrelease_verdict_rejected(self):
        study, records, gold = make_fixture([("correct", "infra")])
        forged = replace(gold[0], policy=C)
        with self.assertRaisesRegex(ValueError, "abstained, failed"):
            audit_attrition_sign_sensitivity(study, records,
                                             gold + (forged,), T, C)

    def test_mismatched_released_patch_digest_denied(self):
        study, records, gold = make_fixture([("correct", "wrong")])
        edited = (replace(gold[0], patch_sha256="8"*64),) + gold[1:]
        with self.assertRaisesRegex(ValueError, "different from released"):
            audit_attrition_sign_sensitivity(study, records, edited, T, C)

    def test_exceed_any_hard_budget_denied(self):
        study, records, gold = make_fixture([("correct", "wrong")])
        for dimension, value in (("tokens", 501), ("test_calls", 11),
                                 ("gpu_seconds", 10.1), ("cpu_seconds", 10.1),
                                 ("wall_seconds", 20.1)):
            values = {name: getattr(records[0].consumed, name)
                      for name in ("tokens","test_calls","gpu_seconds",
                                   "cpu_seconds","wall_seconds")}
            values[dimension] = value
            changed = (replace(records[0], consumed=RV(**values)),) + records[1:]
            with self.subTest(dimension=dimension), self.assertRaisesRegex(
                    ValueError, "FIVE-resource"):
                audit_attrition_sign_sensitivity(study, changed, gold, T, C)

    def test_exhaustive_small_risk_bound_denominators_are_sharp(self):
        # Independent brute-force counterfactual reference: no-release,
        # correct-release or wrong-release for every infra-missing cell.
        for r in range(4):
            for wrong in range(r+1):
                for unknown in range(4):
                    rows = []
                    verdicts = {}
                    for i in range(r+unknown+1):
                        if i < r:
                            termination = "release"
                            truth = i >= r - wrong
                        elif i < r+unknown:
                            termination = "infrastructure_failure"
                            truth = None
                        else:
                            termination = "abstain"
                            truth = None
                        name = f"fake-{i}"
                        patch = format(i+1, "064x")
                        row = PolicyRunReceipt(
                            name, name, "model", T, 17, "budget",
                            "a"*40, "b"*40, "c"*64, "d"*64,
                            USED, termination,
                            patch if termination == "release" else None,
                            "e"*64,
                        )
                        rows.append(row)
                        if termination == "release":
                            verdicts[row.key] = EvaluatorVerdict(
                                name, "model", T, 17, "budget",
                                patch, "f"*64, not truth, "9"*64,
                            )
                    # First r-w releases are correct and last w wrong.
                    measured = _arm(T, tuple(rows), verdicts)
                    expected = exact_conditional_risk(r, wrong, unknown)
                    with self.subTest(r=r, wrong=wrong, unknown=unknown):
                        self.assertEqual(measured.wrong_release_risk_bounds, expected)
                        self.assertEqual(
                            measured.observed_wrong_release_risk,
                            wrong/r if r else None)
                        self.assertEqual(
                            measured.release_coverage_bounds,
                            (r/len(rows), (r+unknown)/len(rows)))
                        self.assertEqual(
                            measured.full_task_success_bounds,
                            ((r-wrong)/len(rows),
                             (r-wrong+unknown)/len(rows)))

    def test_exhaustive_small_two_pair_itt_signs_match_all_binary_completions(self):
        status = ("correct", "wrong", "abstain", "infra", "timeout", "safety")
        # 6^2 statuses for one paired task, including both policies missing.
        for t_state, c_state in product(status, repeat=2):
            data = [(t_state, c_state)]
            found = sign_audit(data)
            options = {
                "infra": (0, 1), "correct": (1,),
                "wrong": (0,), "abstain": (0,),
                "timeout": (0,), "safety": (0,),
            }
            realized = sorted({t - c for t in options[t_state]
                               for c in options[c_state]})
            self.assertEqual(
                (found.lower_difference_numerator,
                 found.upper_difference_numerator),
                (realized[0], realized[-1]))
            labels = tuple(k for k, v in (
                ("NEGATIVE", any(x < 0 for x in realized)),
                ("ZERO", 0 in realized),
                ("POSITIVE", any(x > 0 for x in realized)),
            ) if v)
            self.assertEqual(found.attainable_effect_signs, labels)

    def test_no_oracle_secret_or_empirical_certificate_in_report(self):
        x = sign_audit([("correct", "infra")])
        payload = json.dumps(asdict(x), sort_keys=True)
        self.assertNotIn("oracle_artifact_sha256", payload)
        self.assertNotIn("patch_sha256", payload)
        self.assertFalse(x.named_lineages_independently_authenticated)
        self.assertFalse(x.oracle_independently_authenticated)
        self.assertFalse(x.real_experiment_proven)
        self.assertIn("NOT_A_REAL_RESULT", x.stage)


if __name__ == "__main__":
    unittest.main()
