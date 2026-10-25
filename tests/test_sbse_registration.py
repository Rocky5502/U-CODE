"""Prospective study protocol is selection/analysis design, NEVER outcomes."""
from copy import deepcopy
import json
import unittest

from scripts.validate_sbse_protocol import (
    PROTOCOL, SELECTED, validate_prospective_protocol,
)


class ProspectiveSBSERegistrationTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        self.models = json.loads(SELECTED.read_text(encoding="utf-8"))

    def check(self):
        return validate_prospective_protocol(self.spec, self.models)

    def test_user_selected_six_and_eight_competitors(self):
        v = self.check()
        self.assertEqual(v["user_selected_model_checkpoints"], 6)
        self.assertEqual(v["prospectively_listed_policies"], 8)

    def test_zero_tasks_results_and_external_baselines_admitted(self):
        r = self.check()
        for key in ("qualified_tasks", "independent_oracle_results",
                    "external_comparator_adapters_implemented",
                    "measured_policy_effects"):
            self.assertEqual(r[key], 0)

    def test_all_models_preserved_even_if_hardware_uncertain(self):
        self.spec["model_ids"].pop()
        with self.assertRaisesRegex(ValueError, "six"):
            self.check()

    def test_identity_drift_or_duplicate_rejected(self):
        self.spec["model_ids"][1] = self.spec["model_ids"][0]
        with self.assertRaisesRegex(ValueError, "six"):
            self.check()

    def test_cannot_silently_omit_selective_or_mcts_baselines(self):
        self.spec["policy_ids"].remove("mcts_search")
        with self.assertRaisesRegex(ValueError, "eight"):
            self.check()

    def test_external_method_names_cannot_substitute_an_implemented_control(self):
        self.spec["policy_ids"][2] = "RETRACE"
        with self.assertRaisesRegex(ValueError, "eight"):
            self.check()

    def test_equal_treatment_control_not_accepted(self):
        self.spec["primary_treatment"] = "no_uncertainty_search"
        with self.assertRaisesRegex(ValueError, "must differ"):
            self.check()

    def test_no_unqualified_task_can_appear_in_protocol(self):
        self.spec["qualified_task_ids"] = ["merged-pr-is-not-a-test"]
        with self.assertRaisesRegex(ValueError, "unqualified"):
            self.check()

    def test_no_fake_result_flag_can_be_set(self):
        self.spec["results_measured"] = True
        with self.assertRaisesRegex(ValueError, "unqualified"):
            self.check()

    def test_hypothetical_cap_cannot_be_marked_frozen(self):
        self.spec["final_budget_caps_frozen"] = True
        with self.assertRaisesRegex(ValueError, "remain false"):
            self.check()

    def test_no_quiet_fake_sandbox_attestation(self):
        self.spec["runner_isolated_and_attested"] = True
        with self.assertRaisesRegex(ValueError, "remain false"):
            self.check()

    def test_all_five_cost_budgets_required(self):
        del self.spec["planned_resource_caps_example_not_executed"]["B_pilot_illustrative"]["gpu_seconds"]
        with self.assertRaisesRegex(ValueError, "five budget"):
            self.check()

    def test_negative_budget_forbidden(self):
        self.spec["planned_resource_caps_example_not_executed"]["B_pilot_illustrative"]["wall_seconds"] = -1
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            self.check()


if __name__ == "__main__":
    unittest.main()
