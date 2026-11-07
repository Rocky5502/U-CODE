"""Adversarial tests of V5: continuity is not empirical task admission."""
from copy import deepcopy
import json
import unittest

from scripts.validate_v5_handoff import MANIFEST, ROOT, audit_v5_handoff


class V5HandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(MANIFEST.read_text("utf-8"))
        cls.markdown = (ROOT / cls.record["document"]).read_text("utf-8")

    def check(self, record=None, doc=None):
        return audit_v5_handoff(
            self.record if record is None else record,
            self.markdown if doc is None else doc,
        )

    def test_historical_ci_and_roles_are_safely_pinned(self):
        out = self.check()
        self.assertEqual(out["dated_offline_tests_per_python_version"], 1515)
        self.assertEqual(out["virtual_review_perspectives_not_real_reviewers"], 17)
        self.assertTrue(out["recheck_live_github_and_ci"])

    def test_no_external_approvals_inherited_from_source_pins(self):
        out = self.check()
        self.assertEqual(out["remaining_php_go_independent_gates"], 16)
        self.assertEqual(out["independently_admitted_tasks"], 0)
        self.assertEqual(out["measured_real_effects"], 0)

    def test_reject_forged_new_task_admission(self):
        bad = deepcopy(self.record)
        bad["independently_admitted_tasks"] = 1
        with self.assertRaisesRegex(ValueError, "fabricated admission"):
            self.check(record=bad)

    def test_reject_forged_oracle_or_model(self):
        for field in ("sealed_functional_oracles", "qualified_model_checkpoints"):
            bad = deepcopy(self.record)
            bad[field] = 1
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "fabricated admission"):
                self.check(record=bad)

    def test_reject_claimed_experiment_effect(self):
        bad = deepcopy(self.record)
        bad["real_policy_effects"] = 1
        with self.assertRaisesRegex(ValueError, "fabricated admission"):
            self.check(record=bad)

    def test_reject_claimed_overleaf_sync(self):
        bad = deepcopy(self.record)
        bad["live_overleaf_sync_not_established"] = False
        with self.assertRaisesRegex(ValueError, "journal-readiness"):
            self.check(record=bad)

    def test_reject_missing_original_role(self):
        bad = self.markdown.replace("| **R16 — Meta-review", "| **RXX — Meta-review")
        with self.assertRaisesRegex(ValueError, "role missing: R16"):
            self.check(doc=bad)

    def test_reject_missing_business_rules_blob(self):
        bad = self.markdown.replace(
            "e71288e3127cb66f2471a5ddd2800092db0552cc", "MISSING_BLOB"
        )
        with self.assertRaisesRegex(ValueError, "original_go_business_rules_blob|e71288"):
            self.check(doc=bad)

    def test_reject_modified_original_base_identity(self):
        bad = deepcopy(self.record)
        bad["original_go_base"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "original-source identity"):
            self.check(record=bad)

    def test_reject_dropped_policy_arm(self):
        bad = self.markdown.replace("`replay_search`", "REMOVED_ARM")
        with self.assertRaisesRegex(ValueError, "replay_search"):
            self.check(doc=bad)

    def test_reject_missing_independent_budget_meter(self):
        bad = self.markdown.replace("`gpu_seconds`", "GPU_METER_DELETED")
        with self.assertRaisesRegex(ValueError, "gpu_seconds"):
            self.check(doc=bad)

    def test_reject_misleading_historical_ci(self):
        bad = deepcopy(self.record)
        bad["snapshot_first_party_tests_each"] = 9000
        with self.assertRaisesRegex(ValueError, "historical GitHub evidence"):
            self.check(record=bad)

    def test_reject_missing_first_real_pilot_priority(self):
        bad = self.markdown.replace("P0-1", "P0_REMOVED")
        with self.assertRaisesRegex(ValueError, "P0-1"):
            self.check(doc=bad)


if __name__ == "__main__":
    unittest.main()
