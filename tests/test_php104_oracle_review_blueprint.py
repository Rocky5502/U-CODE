"""Adversarial tests for public, unsealed PHP #104 oracle-review blueprint."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from ucode.php104_oracle_review_blueprint import verify_php104_oracle_blueprint

ROOT = Path(__file__).resolve().parents[1]
ADMISSION = ROOT / "data/admission"
BLUEPRINT = ADMISSION / "2026-10-28/php104_oracle_review_blueprint_PUBLIC_NO_GOLD.json"
CONTRACT = ADMISSION / "2026-10-28/php104_base_source_contract_leads.json"
CHRONOLOGY = ADMISSION / "2026-10-27/two_candidate_issue_chronology_metadata.json"
TREES = ADMISSION / "2026-10-27/two_candidate_pre_fix_tree_inventory.json"
DOSSIERS = ADMISSION / "2026-10-25/pilot_dossiers.jsonl"


class PHP104OracleBlueprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blueprint = json.loads(BLUEPRINT.read_text("utf-8"))
        cls.contract = json.loads(CONTRACT.read_text("utf-8"))
        cls.chronology = json.loads(CHRONOLOGY.read_text("utf-8"))
        cls.trees = json.loads(TREES.read_text("utf-8"))
        cls.dossiers = [json.loads(x) for x in DOSSIERS.read_text("utf-8").splitlines() if x.strip()]

    def check(self, x=None, contract=None, chronology=None, trees=None):
        return verify_php104_oracle_blueprint(
            self.blueprint if x is None else x,
            self.contract if contract is None else contract,
            self.chronology if chronology is None else chronology,
            self.trees if trees is None else trees,
            self.dossiers,
        )

    def test_current_blueprint_is_unapproved_and_unexecuted(self):
        out = self.check()
        self.assertEqual(out["base_commit_predates_parent_seconds"], 2661)
        self.assertEqual(out["prospective_oracle_case_families"], 10)
        self.assertEqual(out["source_notice_files_observed"], 4)
        self.assertEqual(out["qualified_executable_tasks"], 0)
        self.assertEqual(out["sealed_hidden_oracles"], 0)
        self.assertEqual(out["public_gold_output_bytes"], 0)
        self.assertFalse(out["php_code_executed"])
        self.assertFalse(out["policy_input_authorized"])
        self.assertFalse(out["source_file_rights_approved"])

    def test_gold_keys_and_private_test_contents_cannot_enter_blueprint(self):
        for key in ("gold_tests", "solution_patch", "expected_patch",
                    "oracle_results", "private_test_path", "oracle_sha256",
                    "reviewer_attestation", "post_fix_base", "expected_output"):
            x = deepcopy(self.blueprint)
            x[key] = "SECRET"
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "schema drift"):
                self.check(x)

    def test_oracle_case_does_not_accept_expected_outputs(self):
        for key in ("expected_path", "expected_success", "test_source",
                    "gold_patch", "private_oracle_id", "reviewer_name"):
            x = deepcopy(self.blueprint)
            x["oracle_case_families"][0][key] = "SECRET"
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "answer leakage"):
                self.check(x)

    def test_self_promotion_is_impossible(self):
        keys = (
            "source_file_rights_adjudicated", "original_issue_text_sealed",
            "independent_specification_reviewed", "oracle_independently_authored",
            "oracle_sealed_outside_repository", "sandbox_attested",
            "execution_metering_attested", "task_admitted", "php_executed",
        )
        for key in keys:
            x = deepcopy(self.blueprint)
            x[key] = True
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "cannot self-approve"):
                self.check(x)

    def test_hidden_golds_in_any_case_always_rejected(self):
        x = deepcopy(self.blueprint)
        x["oracle_case_families"][-1]["gold_output_included"] = True
        with self.assertRaisesRegex(ValueError, "never be stored"):
            self.check(x)

    def test_do_not_claim_full_oracle_implementation(self):
        x = deepcopy(self.blueprint)
        x["oracle_case_families"][0]["stage"] = "SEALED_ORACLE_READY"
        with self.assertRaisesRegex(ValueError, "cannot claim executed"):
            self.check(x)

    def test_wrong_case_witness_cannot_be_substituted(self):
        x = deepcopy(self.blueprint)
        x["oracle_case_families"][6]["witness_ids"] = [
            "CACHE_TEST_FIXTURE_LAYOUT_DUPLICATION"]
        with self.assertRaisesRegex(ValueError, "exact pre-fix evidence"):
            self.check(x)

    def test_duplicate_missing_or_unknown_case_rejected(self):
        x = deepcopy(self.blueprint)
        x["oracle_case_families"][1] = deepcopy(x["oracle_case_families"][0])
        with self.assertRaisesRegex(ValueError, "repeated|duplicate"):
            self.check(x)
        x = deepcopy(self.blueprint)
        x["oracle_case_families"] = x["oracle_case_families"][:-1]
        with self.assertRaisesRegex(ValueError, "ten independent-review"):
            self.check(x)
        x = deepcopy(self.blueprint)
        x["oracle_case_families"][0]["case_id"] = "POST_PR_GOLD"
        with self.assertRaisesRegex(ValueError, "unregistered"):
            self.check(x)

    def test_license_not_a_self_authorized_file_level_permission(self):
        for field, val in (
            ("root_license_blob_sha", "f"*40),
            ("root_license_observed", "RIGHTS_CLEARED"),
            ("base_commit", "f"*40),
        ):
            x = deepcopy(self.blueprint)
            x[field] = val
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(x)

    def test_notice_tampering_or_injected_rights_fields_fails_closed(self):
        x = deepcopy(self.blueprint)
        x["copyright_notice_observations"][0]["blob_sha"] = "f"*40
        with self.assertRaisesRegex(ValueError, "not pinned"):
            self.check(x)
        x = deepcopy(self.blueprint)
        x["copyright_notice_observations"][0]["license_granted"] = True
        with self.assertRaisesRegex(ValueError, "confidential data"):
            self.check(x)
        x = deepcopy(self.blueprint)
        x["copyright_notice_observations"][0]["notice_type"] = "MIT_CLEARANCE"
        with self.assertRaisesRegex(ValueError, "not pinned"):
            self.check(x)

    def test_unknown_or_duplicate_notice_file_rejected(self):
        x = deepcopy(self.blueprint)
        x["copyright_notice_observations"][1] = deepcopy(x["copyright_notice_observations"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check(x)
        x = deepcopy(self.blueprint)
        x["copyright_notice_observations"][0]["path"] = "../secrets.env"
        with self.assertRaisesRegex(ValueError, "unknown"):
            self.check(x)

    def test_source_commit_must_precede_parent_issue(self):
        x = deepcopy(self.blueprint)
        x["base_commit_time"] = "2026-10-22T22:52:01Z"
        with self.assertRaisesRegex(ValueError, "predate issue"):
            self.check(x)
        x = deepcopy(self.blueprint)
        x["base_commit_time"] = "2026-10-22T22:07:39"
        with self.assertRaisesRegex(ValueError, "timezone aware"):
            self.check(x)

    def test_underlying_source_contract_cannot_be_changed(self):
        x = deepcopy(self.contract)
        x["parent_issue_created_at"] = "2026-10-22T22:55:41Z"
        with self.assertRaisesRegex(ValueError, "order invalid|predate"):
            self.check(contract=x)
        x = deepcopy(self.chronology)
        x["records"][0]["pr_base_sha"] = "f"*40
        with self.assertRaisesRegex(ValueError, "immutable PR SHA"):
            self.check(chronology=x)


if __name__ == "__main__":
    unittest.main()
