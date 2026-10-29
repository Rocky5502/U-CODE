"""Adversarial negative-evidence checks: never authorize local model/task runs."""
from copy import deepcopy
from pathlib import Path
import csv
import json
import unittest

from scripts.check_local_readiness import (
    CONFIG, DATASETS, MODELS, PROTOCOL, validate_local_preflight,
)


class LocalExperimentPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.models = json.loads(MODELS.read_text(encoding="utf-8"))
        cls.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        with DATASETS.open(encoding="utf-8", newline="") as f:
            cls.datasets = list(csv.DictReader(f))

    def check(self, config=None, models=None, protocol=None, datasets=None):
        return validate_local_preflight(
            self.original if config is None else config,
            self.models if models is None else models,
            self.protocol if protocol is None else protocol,
            self.datasets if datasets is None else datasets,
        )

    def test_current_six_models_eight_policies_are_prospective_only(self):
        r = self.check()
        self.assertEqual(r["status"], "BLOCKED_NOT_AUTHORIZED")
        self.assertEqual(len(r["model_ids"]), 6)
        self.assertEqual(len(r["policy_ids"]), 8)
        self.assertEqual(r["external_dataset_candidates"], 13)
        self.assertEqual(r["independently_admitted_tasks"], 0)
        self.assertEqual(r["sealed_oracles"], 0)
        self.assertIsNone(r["experiment_outcomes"])
        self.assertFalse(r["safe_to_execute_third_party_code"])
        self.assertFalse(r["authorized_to_rent_gpu"])
        self.assertEqual(len(r["gates_pending"]), 9)

    def test_no_silent_six_model_substitution_or_reordering(self):
        for mode in ("alter", "swap", "drop"):
            x = deepcopy(self.original)
            if mode == "alter":
                x["planned_model_ids"][0] = "unknown/other"
            elif mode == "swap":
                x["planned_model_ids"][0], x["planned_model_ids"][1] = (
                    x["planned_model_ids"][1], x["planned_model_ids"][0])
            else:
                x["planned_model_ids"].pop()
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "roster"):
                self.check(x)

    def test_no_silent_policy_mutation(self):
        x = deepcopy(self.original)
        x["planned_policy_ids"][0] = "other_bes"
        with self.assertRaisesRegex(ValueError, "policies"):
            self.check(x)
        x = deepcopy(self.original)
        x["primary_treatment"] = "uncertainty_only"
        with self.assertRaisesRegex(ValueError, "primary"):
            self.check(x)

    def test_execution_or_oracle_access_cannot_self_authorize(self):
        for field in ("training_or_trial_approved", "allowed_to_download_weights",
                      "allowed_to_execute_upstream_code",
                      "allowed_to_access_sealed_oracle", "outcomes_measured"):
            x = deepcopy(self.original)
            x[field] = True
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "self-authorize"):
                self.check(x)

    def test_gates_cannot_self_certify(self):
        for key in self.original["gates"]:
            x = deepcopy(self.original)
            x["gates"][key] = True
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "self-certify"):
                self.check(x)

    def test_no_unpinned_weights_or_runtime_path(self):
        for name, value in (
            ("checkpoint_revision", "main"),
            ("tokenizer_revision", "abcdef"),
            ("local_weight_path", "../private"),
            ("quantization", "q4_0"),
            ("engine", "unreviewed-remote-code"),
            ("load_test_verified", True),
        ):
            x = deepcopy(self.original)
            x["local_model_overrides"][0][name] = value
            with self.subTest(field=name), self.assertRaisesRegex(ValueError, "cannot be promoted"):
                self.check(x)

    def test_unknown_keys_or_secret_injection_not_ignored(self):
        x = deepcopy(self.original)
        x["hf_token"] = "secret"
        with self.assertRaisesRegex(ValueError, "schema drift"):
            self.check(x)
        x = deepcopy(self.original)
        x["local_model_overrides"][0]["oracle_path"] = "secrets.json"
        with self.assertRaisesRegex(ValueError, "override schema"):
            self.check(x)

    def test_non_loopback_endpoint_rejected(self):
        for ip in ("0.0.0.0", "192.168.1.11", "https://remote.example"):
            x = deepcopy(self.original)
            x["local_server_address"] = ip
            with self.subTest(ip=ip), self.assertRaisesRegex(ValueError, "loopback"):
                self.check(x)

    def test_fake_gpu_measurements_rejected(self):
        for key, value in (
            ("observed", True), ("gpu_name", "RTX 5070 Ti"),
            ("actual_vram_gb", 16), ("driver_version", "latest"),
        ):
            x = deepcopy(self.original)
            x["hardware_observation"][key] = value
            with self.subTest(field=key), self.assertRaisesRegex(ValueError, "hardware"):
                self.check(x)

    def test_source_registry_cannot_promote_executed_task(self):
        rows = deepcopy(self.datasets)
        rows[0]["local_execution"] = "verified"
        with self.assertRaisesRegex(ValueError, "unexecuted"):
            self.check(datasets=rows)

    def test_canonical_reference_paths_cannot_escape(self):
        x = deepcopy(self.original)
        x["authoritative_model_registry"] = "../temp.json"
        with self.assertRaisesRegex(ValueError, "canonical"):
            self.check(x)

    def test_hardware_unknown_and_no_assignments_stay_unknown(self):
        x = deepcopy(self.original)
        x["experiment_assignments"] = 1
        with self.assertRaisesRegex(ValueError, "no assigned"):
            self.check(x)


if __name__ == "__main__":
    unittest.main()
