"""SYNTHETIC reproducibility checks for fixed-schedule negative control."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from examples.blind_search_smoke import reproduce, CONFIG
from ucode.blind_search import blind_catalog_from_public_manifest


class BlindSearchSmokeTests(unittest.TestCase):
    def test_demo_is_deterministic_not_a_real_result(self):
        self.assertEqual(reproduce(), reproduce())
        r = reproduce()
        self.assertEqual(r["provenance"], "HAND_AUTHORED_SYNTHETIC_NOT_MEASURED")
        self.assertIsNone(r["success_rate"])
        self.assertIsNone(r["wrong_release_risk"])
        self.assertEqual(r["external_code_executions"], 0)
        self.assertEqual(r["hidden_oracle_results"], 0)

    def test_fixture_action_path_repair_after_negative_and_release(self):
        r = reproduce()
        self.assertEqual([x["action"] for x in r["actions"]],
                         ["generate_v1","retrieve_1","test_candidate_v1",
                          "repair_v1","test_candidate_v2","release"])
        self.assertEqual(r["terminal_action"], "release")
        self.assertEqual(r["candidate_patch_sha256"], "b"*64)
        self.assertEqual(r["spent_tokens_fixture"], 37)
        self.assertEqual(r["spent_test_calls_fixture"], 2)

    def test_config_declares_all_five_cost_dimensions_no_oracle_fields(self):
        v = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertIn("SYNTHETIC",v["status"])
        self.assertEqual(len(v["actions"]),5)
        self.assertEqual(len(blind_catalog_from_public_manifest(v["actions"])),5)
        self.assertTrue(all(set(a["cost"])=={
            "tokens","test_calls","gpu_seconds","cpu_seconds","wall_seconds"
        } for a in v["actions"]))
        self.assertNotIn("gold_patch",json.dumps(v))
        self.assertNotIn("oracle_passed",json.dumps(v))

    def test_no_hidden_oracle_may_be_added_to_catalog(self):
        v = json.loads(CONFIG.read_text(encoding="utf-8"))
        actions = deepcopy(v["actions"])
        actions[0]["oracle_passed"] = True
        with self.assertRaisesRegex(ValueError,"oracle leak"):
            blind_catalog_from_public_manifest(actions)


if __name__=="__main__":
    unittest.main()
