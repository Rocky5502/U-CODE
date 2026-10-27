"""Handoff must agree with the real audited data, models and study protocol.

These are structural checks only, NOT external verification of actual tasks,
model loads, live Overleaf, or an authenticated published journal artifact.
"""
from copy import deepcopy
import json
import unittest

from scripts.validate_research_handoff import HANDOFF, validate_handoff_snapshot


class HandoffContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(HANDOFF.read_text("utf-8"))

    def check(self, edits=None):
        return validate_handoff_snapshot(
            deepcopy(self.original) if edits is None else edits)

    def test_actual_handoff_is_complete_and_honest(self):
        got = self.check()
        self.assertEqual(got["metadata_records"], 120)
        self.assertEqual(got["query_language_strata"], 12)
        self.assertEqual(got["independent_task_admissions"], 0)
        self.assertEqual(got["real_model_effects"], 0)
        self.assertFalse(got["live_overleaf_synced"])
        self.assertGreaterEqual(got["unresolved_research_work_packages"], 9)

    def test_cannot_forge_task_admission(self):
        v = deepcopy(self.original)
        v["source_data"]["qualified_executable_tasks"] = 12
        with self.assertRaisesRegex(ValueError, "count differs"):
            self.check(v)

    def test_cannot_confuse_search_language_with_changed_code_language(self):
        v = deepcopy(self.original)
        v["source_data"]["labels_are_query_strata_not_verified_changed_language"] = False
        with self.assertRaisesRegex(ValueError, "search-language"):
            self.check(v)

    def test_cannot_claim_models_ran(self):
        v = deepcopy(self.original)
        v["models"]["real_inference_runs_verified"] = 6
        with self.assertRaisesRegex(ValueError, "uncorroborated"):
            self.check(v)

    def test_cannot_claim_live_overleaf_sync(self):
        v = deepcopy(self.original)
        v["paper"]["external_live_overleaf_project_synced"] = True
        with self.assertRaisesRegex(ValueError, "uncorroborated"):
            self.check(v)

    def test_cannot_rewrite_primary_study_treatment(self):
        v = deepcopy(self.original)
        v["study"]["primary_treatment"] = "new_unregistered_policy"
        with self.assertRaisesRegex(ValueError, "arm mismatches"):
            self.check(v)

    def test_cannot_drop_5th_budget(self):
        v = deepcopy(self.original)
        v["study"]["resource_vector"].pop()
        with self.assertRaisesRegex(ValueError, "five resource"):
            self.check(v)

    def test_cannot_drop_independent_oracle_gate(self):
        v = deepcopy(self.original)
        v["next_work"] = [w for w in v["next_work"]
                          if w["issue"] != 7]
        with self.assertRaisesRegex(ValueError, "oracle pilot gate"):
            self.check(v)

    def test_each_queue_task_must_have_exit_criteria(self):
        v = deepcopy(self.original)
        v["next_work"][0]["exit_criteria"] = ""
        with self.assertRaisesRegex(ValueError, "acceptance criteria"):
            self.check(v)

    def test_duplicate_work_package_refused(self):
        v = deepcopy(self.original)
        v["next_work"][1]["id"] = v["next_work"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicated"):
            self.check(v)


if __name__ == "__main__":
    unittest.main()
