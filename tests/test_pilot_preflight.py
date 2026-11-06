"""Adversarial real-source PHP/Go preflight tests; never execute either PR.

These are checks on actual historical GitHub metadata ledgers, NOT
measurements of LLM coding success, rights approval, or sealed test validity.
"""
from copy import deepcopy
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
import unittest

from scripts.compile_pilot_preflight import main as preflight_cli
from ucode import pilot_preflight as mod


class RealPilotPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_pilot_preflight()

    def test_two_real_prs_blocked_six_models_eight_policies(self):
        r = self.report
        self.assertEqual(r["candidate_count"], 2)
        self.assertEqual([x["candidate_id"] for x in r["candidates"]], [43, 104])
        self.assertEqual(r["pending_admission_checks"], 16)
        self.assertEqual(r["qualified_executable_tasks"], 0)
        self.assertEqual(r["real_model_runs"], 0)
        self.assertEqual(r["drpa_real_task_evaluations"], 0)
        self.assertEqual(r["model_slots_registered_not_qualified"], 6)
        self.assertEqual(r["policy_slots_registered_not_executed"], 8)
        self.assertEqual(r["primary_treatment"], "ucode_conditional_bes")
        self.assertEqual(r["primary_comparator"], "no_uncertainty_search")
        self.assertFalse(r["matched_real_run_matrix_frozen"])
        self.assertIsNone(r["confirmed_primary_effect"])
        self.assertFalse(r["external_source_executed"])

    def test_identity_and_source_era_scope_are_explicit(self):
        rows = {x["candidate_id"]: x for x in self.report["candidates"]}
        self.assertEqual(rows[43]["repository"], "PlayHuai/eighty-point-huai-an")
        self.assertEqual(rows[104]["repository"], "mvdbos/php-spider")
        self.assertEqual(rows[43]["task_scope"], "declared_microtask")
        self.assertEqual(rows[104]["task_scope"], "full_pr")
        self.assertIn("MICROTASK", rows[43]["source_era_spec_issue"])
        self.assertIn("NOT_ARCHIVED", rows[104]["source_era_spec_issue"])
        for x in rows.values():
            self.assertEqual(x["open_gate_count"], 8)
            self.assertTrue(x["prospective_only"])
            self.assertFalse(x["external_execution_allowed"])
            self.assertFalse(x["independently_qualified"])
            self.assertEqual(len(x["dossier_sha256"]), 64)
            self.assertIn("no_separate_evaluator_oracle",
                          x["evaluator_registration_blockers"])

    def test_output_is_reproducible_and_contains_no_hidden_gold(self):
        first = json.dumps(self.report, sort_keys=True, separators=(",", ":"))
        second = json.dumps(mod.build_pilot_preflight(),
                            sort_keys=True, separators=(",", ":"))
        self.assertEqual(first, second)
        self.assertNotIn("oracle_passed", first)
        self.assertNotIn("gold_output_included", first)
        self.assertFalse(self.report["hidden_oracle_values_exposed"])

    def test_strict_cli_fails_instead_of_pretending_approval(self):
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(preflight_cli(["--require-ready"]), 2)
        r = json.loads(output.getvalue())
        self.assertEqual(r["qualified_executable_tasks"], 0)
        self.assertIn("BLOCKED", r["stage"])

    def test_normal_cli_explicitly_reports_research_only(self):
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(preflight_cli([]), 0)
        r = json.loads(output.getvalue())
        self.assertEqual(r["drpa_real_task_evaluations"], 0)

    def changed_json(self, match: str, mutation):
        original = mod._json
        def substitute(path):
            obj = original(path)
            if match in path.name:
                obj = deepcopy(obj)
                mutation(obj)
            return obj
        with patch.object(mod, "_json", side_effect=substitute):
            return mod.build_pilot_preflight()

    def test_forged_php_license_or_oracle_claim_rejected(self):
        for field in ("executable_task_admitted", "source_rights_cleared",
                      "held_out_oracle_approved"):
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "PHP source-era"):
                self.changed_json("php104_base_source_contract_leads",
                                  lambda obj: obj.__setitem__(field, True))

    def test_forced_php_gold_in_public_blueprint_rejected(self):
        with self.assertRaisesRegex(ValueError, "PHP public blueprint"):
            self.changed_json(
                "php104_oracle_review_blueprint_PUBLIC",
                lambda obj: obj["oracle_case_families"][0].__setitem__(
                    "gold_output_included", True),
            )

    def test_go_pre_fix_spec_replacement_and_false_admission_rejected(self):
        for field, value in (("spec_blob_sha", "0"*40),
                             ("experiment_eligible", True)):
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "Go pre-fix"):
                self.changed_json("go43_immutable_pre_fix_spec_blob",
                                  lambda obj: obj.__setitem__(field, value))

    def test_unregistered_new_ninth_policy_and_seed_or_model_fabrication_rejected(self):
        for field, value in (("policy_ids", ["rogue"]*9),
                             ("results_measured", True),
                             ("seeds_frozen", True)):
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "confirmatory protocol"):
                self.changed_json(
                    "confirmatory_sbse_protocol",
                    lambda obj: obj.__setitem__(field, value))

    def test_fake_model_checkpoint_cannot_be_called_qualified(self):
        with self.assertRaisesRegex(ValueError, "model plan"):
            self.changed_json(
                "accepted_six_model_study",
                lambda obj: obj["models"][0].__setitem__(
                    "checkpoint_revision", "a"*40))

    def test_mutated_prospective_evaluator_registration_is_rejected(self):
        original = mod._jsonl
        def substitute(path):
            records = original(path)
            if path.name == "prospective_oracle_registrations.jsonl":
                rows = [deepcopy(x) for x in records]
                rows[0]["task_base_sha"] = "f"*40
                return tuple(rows)
            return records
        with patch.object(mod, "_jsonl", side_effect=substitute):
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                mod.build_pilot_preflight()

    def test_unknown_oracle_field_cannot_enter_public_registration(self):
        original = mod._jsonl
        def substitute(path):
            records = original(path)
            if path.name == "prospective_oracle_registrations.jsonl":
                rows = [deepcopy(x) for x in records]
                rows[0]["hidden_gold_patch"] = "secret"
                return tuple(rows)
            return records
        with patch.object(mod, "_jsonl", side_effect=substitute):
            with self.assertRaisesRegex(ValueError, "unknown registration fields"):
                mod.build_pilot_preflight()


if __name__ == "__main__":
    unittest.main()
