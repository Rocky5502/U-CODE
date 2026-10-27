"""Repo source-tree provenance tests, source-only and nonexecuting."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from ucode.pre_fix_tree_audit import (
    check_pre_fix_tree_inventory, verify_tree_snapshot,
)

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "data/admission/2026-10-27/two_candidate_pre_fix_tree_inventory.json"
DOSSIERS = ROOT / "data/admission/2026-10-25/pilot_dossiers.jsonl"


class PreFixTreeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(TREE.read_text("utf-8"))
        cls.dossiers = [json.loads(x) for x in DOSSIERS.read_text(
            "utf-8").splitlines() if x]

    def check(self, snapshot=None):
        return check_pre_fix_tree_inventory(
            self.source if snapshot is None else snapshot,
            self.dossiers)

    def test_read_only_php_and_go_file_identity_evidence(self):
        result = verify_tree_snapshot(TREE, DOSSIERS)
        self.assertEqual(result["inventory_records"], 2)
        self.assertEqual(result["read_only_tree_paths_observed"], 4)
        self.assertEqual(result["toolchain_config_paths_observed"], 3)
        self.assertEqual(result["scientifically_admitted_tasks"], 0)
        self.assertEqual(result["real_builds_executed"], 0)

    def test_actual_base_trees_distinct_from_git_commit_hashes(self):
        output = self.check()
        self.assertTrue(all(
            entry["base_commit"] != entry["base_tree_sha"]
            for entry in output["records"]))

    def test_modified_base_commit_rejected(self):
        x = deepcopy(self.source)
        x["records"][0]["base_commit"] = "a"*40
        with self.assertRaisesRegex(ValueError, "canonical PR"):
            self.check(x)

    def test_forged_license_root_blob_rejected(self):
        x = deepcopy(self.source)
        x["records"][0]["baseline_root_license_blob_sha"] = "a"*40
        with self.assertRaisesRegex(ValueError, "canonical PR/license"):
            self.check(x)

    def test_using_commit_sha_as_git_tree_sha_rejected(self):
        x = deepcopy(self.source)
        x["records"][0]["base_tree_sha"] = x["records"][0]["base_commit"]
        with self.assertRaisesRegex(ValueError, "actual Git tree"):
            self.check(x)

    def test_untracked_changed_production_path_rejected(self):
        x = deepcopy(self.source)
        x["records"][0]["observed_existing_source"][0]["path"] = "secret.conf"
        with self.assertRaisesRegex(ValueError, "changed production"):
            self.check(x)

    def test_bogus_existing_file_blob_sha_rejected(self):
        x = deepcopy(self.source)
        x["records"][0]["observed_existing_source"][0]["git_blob_sha"] = "NOT_A_SHA"
        with self.assertRaisesRegex(ValueError, "blob"):
            self.check(x)

    def test_expected_new_file_cannot_also_exist_at_base(self):
        x = deepcopy(self.source)
        x["records"][0]["observed_expected_new_source_not_at_base"].append(
            x["records"][0]["observed_existing_source"][0]["path"])
        with self.assertRaisesRegex(ValueError, "contradicts"):
            self.check(x)

    def test_truncated_tree_results_rejected(self):
        x = deepcopy(self.source)
        x["records"][1]["tree_recursion_truncated"] = True
        with self.assertRaisesRegex(ValueError, "complete plausible"):
            self.check(x)

    def test_unauthorized_real_build_claim_rejected(self):
        for key in ("real_build_executed", "source_code_downloaded",
                    "source_file_redistribution_approved",
                    "independent_oracle_verified", "experiment_eligible"):
            x = deepcopy(self.source)
            x["records"][0][key] = True
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "do not authorize"):
                    self.check(x)

    def test_hidden_patch_injection_rejected(self):
        x = deepcopy(self.source)
        x["records"][0]["gold_patch"] = "unexpected"
        with self.assertRaisesRegex(ValueError, "schema drift"):
            self.check(x)

    def test_absolute_path_traversal_rejected(self):
        for path in ("../foo.php", "/etc/passwd", "a/../code.py", "D:/key", "a\\b"):
            x = deepcopy(self.source)
            x["records"][0]["toolchain_metadata"][0]["path"] = path
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, "path"):
                    self.check(x)

    def test_duplicate_candidate_tree_record_rejected(self):
        x = deepcopy(self.source)
        x["records"][1] = deepcopy(x["records"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check(x)


if __name__ == "__main__":
    unittest.main()
