"""V4 takeover stays complete, historically grounded and never self-approves."""
from copy import deepcopy
import json
import unittest

from scripts.validate_v4_handoff import MANIFEST, audit_v4_handoff


class V4HandoffScientificIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(MANIFEST.read_text("utf-8"))

    def audit(self, data=None):
        return audit_v4_handoff(self.source if data is None else data)

    def test_verified_baseline_is_explicitly_historical(self):
        out=self.audit()
        self.assertEqual(out["virtual_roles"],17)
        self.assertEqual(out["pr_discovery_records"],120)
        self.assertEqual(out["baseline_tests_per_version"],1115)
        self.assertTrue(out["new_main_ci_must_be_rechecked"])

    def test_all_observed_study_results_remain_zero(self):
        out=self.audit()
        self.assertEqual(out["independently_admitted_tasks"],0)
        self.assertEqual(out["actual_model_experiments"],0)
        self.assertEqual(out["real_effectiveness_measured"],0)

    def test_cannot_promote_source_lead_into_runnable_task(self):
        bad=deepcopy(self.source)
        bad["observed_dataset"]["independently_approved_executable_tasks"]=1
        with self.assertRaisesRegex(ValueError,"data counters"):
            self.audit(bad)

    def test_cannot_relabel_query_languages_as_more_strata(self):
        bad=deepcopy(self.source)
        bad["observed_dataset"]["search_language_strata"]=13
        with self.assertRaisesRegex(ValueError,"data counters"):
            self.audit(bad)

    def test_cannot_forge_model_results(self):
        bad=deepcopy(self.source)
        bad["prospective_study"]["real_model_inferences_verified"]=1
        with self.assertRaisesRegex(ValueError,"incorrectly promoted"):
            self.audit(bad)

    def test_cannot_fake_live_overleaf(self):
        bad=deepcopy(self.source)
        bad["prospective_study"]["live_overleaf_synced"]=True
        with self.assertRaisesRegex(ValueError,"incorrectly promoted"):
            self.audit(bad)

    def test_cannot_forge_complete_sandbox(self):
        bad=deepcopy(self.source)
        bad["prospective_study"]["runner_security_attested"]=True
        with self.assertRaisesRegex(ValueError,"incorrectly promoted"):
            self.audit(bad)

    def test_cannot_delete_one_of_seventeen_original_roles(self):
        bad=deepcopy(self.source)
        bad["original_expert_roles"].remove("R12")
        with self.assertRaisesRegex(ValueError,"roles"):
            self.audit(bad)

    def test_cannot_rewrite_original_protocol_treatment(self):
        bad=deepcopy(self.source)
        bad["prospective_study"]["primary_treatment"]="unregistered_oracle"
        with self.assertRaisesRegex(ValueError,"incorrectly promoted"):
            self.audit(bad)

    def test_five_hard_budget_components_not_collapsed(self):
        bad=deepcopy(self.source)
        bad["five_resource_fields"].remove("gpu_seconds")
        with self.assertRaisesRegex(ValueError,"resource dimension"):
            self.audit(bad)

    def test_dated_ci_not_promoted_to_latest_ci_forever(self):
        bad=deepcopy(self.source)
        bad["status_must_be_rechecked_on_next_chat"]=False
        with self.assertRaisesRegex(ValueError,"current CI"):
            self.audit(bad)

    def test_required_first_gate_cannot_be_dropped(self):
        bad=deepcopy(self.source)
        bad["priority_first_unblocked_sprint"]="Run models on unreviewed PHP immediately"
        with self.assertRaisesRegex(ValueError,"task/oracle priority"):
            self.audit(bad)

    def test_invalid_handoff_path_fails_closed(self):
        bad=deepcopy(self.source)
        bad["document"]="docs/missing_file.md"
        with self.assertRaisesRegex(ValueError,"canonical V4"):
            self.audit(bad)


if __name__=="__main__":
    unittest.main()
