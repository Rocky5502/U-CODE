"""Adversarial, entirely first-party phase-0 future-experiment preparation."""
from __future__ import annotations

from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import ucode.real_trial_phase0 as phase
from scripts.prepare_real_experiment_phase0 import main as cli
from ucode.model_readiness import ModelReadiness


class RealExperimentPhaseZeroTests(unittest.TestCase):
    def test_default_metadata_preflight_does_not_start_an_experiment(self):
        with patch.object(phase.subprocess, "run") as command:
            report = phase.build_real_trial_phase0()
        command.assert_not_called()
        self.assertEqual(report["registered_model_count"], 6)
        self.assertEqual(report["registered_policy_slots"], 8)
        self.assertEqual(report["qualified_model_checkpoints"], 0)
        self.assertEqual(report["gates_pending_php_and_go"], 16)
        self.assertEqual(report["approved_real_tasks"], 0)
        self.assertEqual(report["approved_hidden_oracles"], 0)
        self.assertEqual(report["actual_task_assignments"], 0)
        self.assertIsNone(report["real_success_rate"])
        self.assertFalse(report["real_trial_authorized"])
        self.assertEqual(report["local_hardware_survey"]["state"],
                         "NOT_PROBED_OPT_IN_REQUIRED")

    def test_default_illustrative_cap_is_five_independent_dimensions(self):
        data = phase.build_real_trial_phase0()
        hyp = data["hypothetical_capacity_scenario_not_approved_or_scheduled"]
        self.assertEqual(hyp["one_seed_six_model_eight_policy_slots"], 48)
        self.assertEqual(hyp["total_hypothetical_slots"], 48)
        self.assertEqual(hyp["aggregate_individual_resource_envelopes_not_measured"], {
            "tokens": 1440000, "test_calls": 960,
            "gpu_seconds": 172800, "cpu_seconds": 86400,
            "wall_seconds": 172800,
        })
        self.assertTrue(hyp["not_an_expected_execution_time_or_cost"])

    def test_three_seed_what_if_is_not_final_protocol(self):
        report = phase.build_real_trial_phase0(
            hypothetical_task_slots=2, hypothetical_seed_count=3)
        hyp = report["hypothetical_capacity_scenario_not_approved_or_scheduled"]
        self.assertEqual(hyp["illustrative_seeds_used"], [11, 29, 47])
        self.assertEqual(hyp["one_seed_six_model_eight_policy_slots"], 96)
        self.assertEqual(hyp["total_hypothetical_slots"], 288)
        self.assertEqual(hyp["aggregate_individual_resource_envelopes_not_measured"]
                         ["tokens"], 8640000)
        self.assertFalse(report["real_trial_authorized"])

    def test_bad_hypothetical_sizes_rejected(self):
        for key, vals in {
            "hypothetical_task_slots": [0, 21, True, -1, 1.5, "1"],
            "hypothetical_seed_count": [0, 4, True, -1, 1.0, "1"],
        }.items():
            for val in vals:
                with self.subTest(key=key, val=val), self.assertRaises(ValueError):
                    phase.build_real_trial_phase0(**{key: val})

    def test_public_report_is_deterministic(self):
        a = phase.build_real_trial_phase0()
        b = phase.build_real_trial_phase0()
        self.assertEqual(a, b)

    def test_forged_pilot_admission_or_gate_count_fails_closed(self):
        base = phase.build_pilot_preflight()
        for k,v in [
            ("pending_admission_checks", 15),
            ("qualified_executable_tasks", 1),
            ("real_model_runs", 1),
        ]:
            bad = deepcopy(base)
            bad[k] = v
            with self.subTest(key=k), patch.object(
                    phase, "build_pilot_preflight", return_value=bad):
                with self.assertRaisesRegex(ValueError,"blocker inconsistency"):
                    phase.build_real_trial_phase0()

    def test_forged_model_qualification_fails_closed(self):
        selected = phase._read_object(
            phase.ROOT, "configs/accepted_six_model_study_2026-10-25.json")
        originals = phase._read_object(
            phase.ROOT, "configs/models_v2_2026-10-24.json")
        model_rows = list(phase.validate_selected_manifest(selected, originals))
        fake = ModelReadiness(model_rows[0].model_id, True, ())
        model_rows[0] = fake
        with patch.object(phase, "validate_selected_manifest",
                          return_value=tuple(model_rows)):
            with self.assertRaisesRegex(ValueError, "blocker inconsistency"):
                phase.build_real_trial_phase0()

    def test_mutated_registered_model_id_fails(self):
        fn = phase._read_object
        def wrong(root, rel):
            obj = fn(root, rel)
            if rel == "configs/confirmatory_sbse_protocol_2026-10-25.json":
                obj["model_ids"][0] = "NOT_THE_FROZEN_MODEL"
            return obj
        with patch.object(phase, "_read_object", side_effect=wrong):
            with self.assertRaises(ValueError):
                phase.build_real_trial_phase0()

    def test_mutated_illustrative_budget_fails(self):
        fn = phase._read_object
        def wrong(root, rel):
            obj = fn(root, rel)
            if rel == "configs/confirmatory_sbse_protocol_2026-10-25.json":
                obj["planned_resource_caps_example_not_executed"]["B_pilot_illustrative"][
                    "test_calls"] = 0
            return obj
        with patch.object(phase, "_read_object", side_effect=wrong):
            with self.assertRaisesRegex(ValueError,"five-dimensional"):
                phase.build_real_trial_phase0()

    def test_forged_hardware_authentication_flag_rejected(self):
        bad = {"state": "LOCAL_UNAUTHENTICATED_HARDWARE_OBSERVATION_ONLY",
               "local_gpu_report": [],
               "hardware_independently_attested": True}
        with self.assertRaisesRegex(ValueError,"authenticated"):
            phase.build_real_trial_phase0(gpu_survey=bad)

    def test_hardware_survey_rejects_secret_fields_even_caller_supplied(self):
        bad = {"state":"LOCAL_UNAUTHENTICATED_HARDWARE_OBSERVATION_ONLY",
               "local_gpu_report":[{
                   "name_locally_reported":"NVIDIA A100-SXM4-80GB",
                   "memory_total_mib_locally_reported":81251,
                   "driver_locally_reported":"590.12",
                   "serial_number":"PRIVATE_SECRET"}],
               "hardware_independently_attested": False}
        with self.assertRaisesRegex(ValueError,"private GPU"):
            phase.build_real_trial_phase0(gpu_survey=bad)

    def test_missing_host_survey_rows_cannot_claim_observation(self):
        bad = {"state":"LOCAL_UNAUTHENTICATED_HARDWARE_OBSERVATION_ONLY",
               "local_gpu_report": [],
               "hardware_independently_attested": False}
        with self.assertRaisesRegex(ValueError,"observation count"):
            phase.build_real_trial_phase0(gpu_survey=bad)

    def test_nvidia_smi_only_exact_readonly_query(self):
        example = SimpleNamespace(returncode=0, stdout=(
            "NVIDIA RTX 5070 Ti, 16303, 590.12\n"
            "NVIDIA A100-SXM4-80GB, 81251, 550.90.07\n"
        ))
        with patch.object(phase.subprocess, "run", return_value=example) as run:
            result = phase.read_only_nvidia_gpu_survey()
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], list(phase._QUERY))
        self.assertFalse(run.call_args.kwargs.get("shell",False))
        self.assertEqual(result["state"],
                         "LOCAL_UNAUTHENTICATED_HARDWARE_OBSERVATION_ONLY")
        self.assertEqual(len(result["local_gpu_report"]),2)
        self.assertEqual(result["local_gpu_report"][1]["memory_total_mib_locally_reported"],
                         81251)
        self.assertFalse(result["hardware_independently_attested"])
        self.assertNotIn("uuid",json.dumps(result).lower())

    def test_gpu_query_missing_binary_is_not_host_certification(self):
        with patch.object(phase.subprocess,"run",
                          side_effect=FileNotFoundError("no nvidia-smi")):
            r=phase.read_only_nvidia_gpu_survey()
        self.assertEqual(r["state"],"NOT_OBSERVED_LOCAL_CLI_UNAVAILABLE")
        self.assertFalse(r["hardware_independently_attested"])

    def test_gpu_query_returncode_error_is_not_host_certification(self):
        with patch.object(phase.subprocess,"run",
                          return_value=SimpleNamespace(returncode=1,stdout="")):
            r=phase.read_only_nvidia_gpu_survey()
        self.assertEqual(r["state"],"NOT_OBSERVED_LOCAL_CLI_ERROR")

    def test_gpu_query_bad_fields_or_oversized_refused(self):
        for bad in ["NVIDIA A100, abc, 550.11\n",
                    "NVIDIA A100, 81251\n",
                    "GPU, 81251, not_a_driver\n",
                    "GPU, 81251, 550.11, PRIVATE_UUID\n",
                    "GPU, 0, 550.11\n",
                    "z"*9000]:
            with self.subTest(data=bad[:30]), patch.object(
                    phase.subprocess,"run",
                    return_value=SimpleNamespace(returncode=0,stdout=bad)):
                with self.assertRaises(ValueError):
                    phase.read_only_nvidia_gpu_survey()

    def test_gpu_survey_caller_cannot_insert_gpu_code_or_labels(self):
        base=phase.read_only_nvidia_gpu_survey
        with patch.object(phase.subprocess,"run",
                          return_value=SimpleNamespace(
                              returncode=0,stdout="NVIDIA A100, 81251, 550.90\n")):
            gpu=base()
        report=phase.build_real_trial_phase0(gpu_survey=gpu)
        self.assertEqual(report["local_hardware_survey"]["local_gpu_report"][0]
                         ["name_locally_reported"],"NVIDIA A100")
        self.assertFalse(report["real_trial_authorized"])

    def test_default_cli_has_no_subprocess_and_blocks_real_execution(self):
        with patch.object(phase.subprocess,"run") as subprocess_run:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(cli([]), 0)
                self.assertEqual(cli(["--require-real-ready"]), 2)
            subprocess_run.assert_not_called()
        self.assertIn("REAL_TRIAL_PHASE0_METADATA",out.getvalue())
        self.assertIn('"real_trial_authorized": false',out.getvalue())

    def test_opt_in_gpu_cli_is_exactly_one_host_query(self):
        with patch("scripts.prepare_real_experiment_phase0.read_only_nvidia_gpu_survey",
                   return_value={
                       "state":"NOT_OBSERVED_LOCAL_CLI_UNAVAILABLE",
                       "local_gpu_report": [],
                       "hardware_independently_attested": False,
                   }) as probe:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli(["--probe-gpu"]), 0)
            probe.assert_called_once()

    def test_cli_exclusive_output_does_not_replace_private_or_frozen_data(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/"public_status.json"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli(["--output",str(p)]),0)
            self.assertEqual(json.loads(p.read_text())["actual_task_assignments"],0)
            with self.assertRaises(FileExistsError):
                with contextlib.redirect_stdout(io.StringIO()):
                    cli(["--output",str(p)])
            link=Path(tmp)/"bad_symlink.json"
            link.symlink_to(p)
            with self.assertRaisesRegex(ValueError,"symlink"):
                with contextlib.redirect_stdout(io.StringIO()):
                    cli(["--output",str(link)])

    def test_operator_budget_bounds_still_no_real_work(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cli(["--hypothetical-tasks","2","--hypothetical-seeds","3"]),0)
        r=json.loads(out.getvalue())
        self.assertEqual(r["hypothetical_capacity_scenario_not_approved_or_scheduled"]
                         ["total_hypothetical_slots"],288)
        self.assertFalse(r["real_trial_authorized"])


if __name__ == "__main__":
    unittest.main()
