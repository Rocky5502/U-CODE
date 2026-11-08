"""Adversarial, first-party source-only Go #43 feasibility review tests.

No Go runtime, external checker, hidden gold, or post-fix solution is used.
"""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import contextlib
import io
import json
import tempfile
import unittest

from scripts.export_go43_spec_feasibility import (
    compile_go43_spec_feasibility, main,
)
from scripts.compile_go43_review_handoff import compile_go43_public_handoff
from ucode.go43_spec_feasibility import (
    build_go43_spec_feasibility_packet,
    conditional_capped_transfer_witness, fractional_hall_witness,
)
from ucode.pilot_preflight import ROOT


class Go43SpecFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blueprint = json.loads((ROOT /
            "data/admission/2026-11-07/go43_pre_fix_oracle_review_blueprint_PUBLIC_NO_GOLD.json"
        ).read_text("utf-8"))
        cls.handoff = compile_go43_public_handoff()

    def packet(self, blueprint=None, handoff=None):
        return build_go43_spec_feasibility_packet(
            self.blueprint if blueprint is None else blueprint,
            self.handoff if handoff is None else handoff,
        )

    def test_toy_conditional_conservation_witness_not_golden_behavior(self):
        x = conditional_capped_transfer_witness()
        self.assertEqual(x["hypothetical_total_credit"], 10)
        self.assertEqual(x["hypothetical_total_capped_debit"], 4)
        self.assertEqual(x["hypothetical_net_points_created"], 6)
        self.assertFalse(x["conserves_sum_under_assumptions"])
        self.assertFalse(x["oracle_result_or_expected_answer"])
        self.assertFalse(x["independent_business_rule_selected"])

    def test_no_universal_inconsistency_claim_when_balances_suffice(self):
        x = conditional_capped_transfer_witness(losing_balances=(5, 5))
        self.assertEqual(x["hypothetical_net_points_created"], 0)
        self.assertTrue(x["conserves_sum_under_assumptions"])

    def test_variable_underfunding_is_exact_and_nonnegative(self):
        x = conditional_capped_transfer_witness(
            credited_winners=2, nominal_points_per_player=7, losing_balances=(0, 6))
        self.assertEqual(x["hypothetical_net_points_created"], 8)
        self.assertEqual(x["hypothetical_total_capped_debit"], 6)

    def test_bad_budgets_cannot_create_plausible_witness(self):
        for args in [
            {"credited_winners": True},
            {"credited_winners": 0},
            {"losing_balances": (1,)},
            {"losing_balances": [2, 2]},
            {"losing_balances": (2, -1)},
            {"losing_balances": (2, True)},
            {"nominal_points_per_player": 1.5},
        ]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                conditional_capped_transfer_witness(**args)

    def test_exact_rational_case_no_rounding_guess(self):
        x = fractional_hall_witness()
        self.assertEqual(x["documented_multiplier_as_fraction"], "3/2")
        self.assertEqual(x["unrounded_nominal_points_exact"], "15/2")
        self.assertTrue(x["requires_noninteger_representation_or_a_rule"])
        self.assertFalse(x["integer_rounding_rule_selected"])

    def test_integer_multiplier_does_not_force_rounding(self):
        x = fractional_hall_witness(base_points=4, multiplier_numerator=3,
                                    multiplier_denominator=2)
        self.assertEqual(x["unrounded_nominal_points_exact"], "6")
        self.assertFalse(x["requires_noninteger_representation_or_a_rule"])

    def test_fractional_input_validation(self):
        for args in [{"base_points": 0}, {"base_points": False},
                     {"multiplier_numerator": -1},
                     {"multiplier_denominator": 0},
                     {"multiplier_denominator": 2.0}]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                fractional_hall_witness(**args)

    def test_six_decision_dependencies_cover_all_twelve_prospective_cases(self):
        p = self.packet()
        self.assertEqual(p["stage"], "GO43_SPEC_CONSISTENCY_REVIEW_ONLY_NOT_EXECUTABLE")
        self.assertEqual(len(p["independent_decision_dependencies"]), 6)
        impacted = set.union(*(set(x["affected_prospective_case_families"])
                               for x in p["independent_decision_dependencies"]))
        self.assertEqual(len(impacted), 12)
        self.assertTrue(p["all_twelve_prospective_cases_require_normativity_review"])
        self.assertFalse(p["case_expected_outputs_included"])
        self.assertFalse(p["external_execution_authorized"])
        self.assertEqual(p["real_go_model_outcomes"], 0)

    def test_dependency_resolution_cannot_be_fabricated(self):
        bad = deepcopy(self.blueprint)
        bad["ambiguity_register"][0]["status"] = "APPROVED_BY_AI"
        with self.assertRaisesRegex(ValueError, "cannot be self-resolved"):
            self.packet(blueprint=bad)

    def test_cannot_insert_expected_oracle_answers(self):
        bad = deepcopy(self.blueprint)
        bad["oracle_case_families"][0]["expected"] = 42
        with self.assertRaisesRegex(ValueError, "gold leakage"):
            self.packet(blueprint=bad)

    def test_public_task_admission_field_still_fails_closed(self):
        bad = deepcopy(self.blueprint)
        bad["task_admitted"] = True
        with self.assertRaisesRegex(ValueError, "cannot grant task admission"):
            self.packet(blueprint=bad)

    def test_historical_blob_swap_rejected(self):
        bad = deepcopy(self.blueprint)
        bad["business_rules_git_blob_sha40"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "unverified Go source"):
            self.packet(blueprint=bad)

    def test_unapproved_handoff_cannot_self_promote(self):
        bad = deepcopy(self.handoff)
        bad["qualified_executable_tasks"] = 1
        with self.assertRaisesRegex(ValueError, "unverified Go source"):
            self.packet(handoff=bad)

    def test_duplicate_case_or_ambiguity_fails(self):
        for field, changed in (
            ("oracle_case_families", "case_id"),
            ("ambiguity_register", "ambiguity_id")):
            bad = deepcopy(self.blueprint)
            bad[field][1][changed] = bad[field][0][changed]
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.packet(blueprint=bad)

    def test_export_reproducible_and_spec_not_resolved(self):
        a = compile_go43_spec_feasibility()
        b = compile_go43_spec_feasibility()
        self.assertEqual(a, b)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "public_no_gold.json"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--output", str(out)]), 0)
                self.assertEqual(main(["--require-spec-resolved"]), 2)
            saved = json.loads(out.read_text("utf-8"))
            self.assertEqual(saved, a)
            self.assertNotIn("reviewer_identity", saved)
            self.assertFalse(saved["task_admitted"])

    def test_public_report_prohibits_symlink_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "original.json"
            original.write_text("do not change", encoding="utf-8")
            alias = Path(tmp) / "alias.json"
            alias.symlink_to(original)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(
                    ValueError, "symlink"):
                main(["--output", str(alias)])
            self.assertEqual(original.read_text("utf-8"), "do not change")


if __name__ == "__main__":
    unittest.main()
