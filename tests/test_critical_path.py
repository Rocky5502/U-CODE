"""Adversarial scientific status checks: NO live tasks or invented outcomes.

All source fixtures are canonical prospective metadata only. Tests never
authenticate an external reviewer, load model weights or execute PR code.
"""
from copy import deepcopy
from hashlib import sha256
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from scripts.export_critical_path import export_critical_path, main as cli
from ucode import critical_path as cp


class CriticalPathAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=cp.ROOT
        cls.pilot=cp.build_pilot_preflight(cls.root)
        cls.protocol=cp._object(cls.root,
            "configs/confirmatory_sbse_protocol_2026-10-25.json")
        cls.models=cp._object(cls.root,
            "configs/accepted_six_model_study_2026-10-25.json")
        cls.gates=cp._object(cls.root,
            "configs/ucode_work_remaining_gates_2026-10-27.json")
        cls.metadata=cp._object(cls.root,
            "data/curated/2026-10-27/frozen_cleaning_summary.json")

    def report(self, **kwargs):
        options={
            "pilot":self.pilot, "protocol":self.protocol,
            "selected":self.models, "gate_register":self.gates,
            "metadata":self.metadata,
        }
        options.update(kwargs)
        return cp.build_critical_path(**options)

    def test_exact_ten_major_exit_criteria_and_four_p0(self):
        r=self.report()
        a=r["milestone_accounting"]
        self.assertEqual(a["total_exit_criteria"],10)
        self.assertEqual(a["independently_verified_complete_exit_criteria"],0)
        self.assertEqual(a["still_without_full_exit_evidence"],10)
        self.assertEqual(a["phase_totals"],{"P0":4,"P1":5,"P2":1})
        self.assertEqual(a["independent_workstreams_possible_now"],
                         ["P0-1","P0-2","P0-3","P0-4"])
        self.assertEqual([x["id"] for x in r["milestones"]],list(cp.IDS))
        self.assertIsNone(a["overall_percent_complete"])
        self.assertIsNone(a["calendar_time_remaining_estimate"])
        self.assertTrue(all(not x["scientific_exit_criterion_independently_verified"]
                            for x in r["milestones"]))

    def test_longest_dependency_chain_is_not_a_time_estimate(self):
        a=self.report()["milestone_accounting"]
        self.assertEqual(a["longest_chain_length_in_milestones"],5)
        self.assertEqual(
            a["one_longest_dependency_chain"],
            ["P0-1","P1-5","P1-8","P1-9","P2-10"])
        self.assertIn("NOT elapsed time",a["interpretation"])

    def test_source_metadata_and_live_pilot_are_crosschecked(self):
        r=self.report()
        self.assertEqual(r["metadata_discovery"],{
            "pr_leads":120,"retrieved_pr_metadata":119,
            "production_source_path_leads":62,
            "prioritized_manual_review_leads":12,
        })
        self.assertEqual(r["independent_pilot_admission"]["open_checks"],16)
        self.assertEqual(r["independent_pilot_admission"]["qualified_executable_tasks"],0)
        self.assertEqual(r["models"]["planned"],6)
        self.assertEqual(r["models"]["checkpoint_revisions_frozen"],0)
        self.assertEqual(r["policies"]["registered"],8)
        self.assertEqual(r["scientific_measurement"]["measured_primary_effect"],None)
        self.assertEqual(r["manuscript"]["verified_publisher_pdf_compiled"],False)
        self.assertEqual(r["manuscript"]["external_live_overleaf_synced"],False)

    def test_model_blockers_reported_by_real_model_readiness_checker(self):
        r=self.report()
        b=r["models"]["unique_blocker_categories"]
        self.assertEqual(b["checkpoint_revision_not_immutable"],6)
        self.assertEqual(b["tokenizer_revision_not_immutable"],6)
        self.assertEqual(b["weights_not_verified"],6)
        self.assertEqual(b["sandbox_not_approved"],6)

    def test_unknown_historical_snapshot_status_not_mistaken_for_current(self):
        g=deepcopy(self.gates)
        g["next_work"][0]["status"]="COMPLETED_BUT_NOT_EXTERNALLY_ATTESTED"
        a=cp.build_critical_path(
            pilot=self.pilot,protocol=self.protocol,selected=self.models,
            gate_register=g,metadata=self.metadata)
        self.assertEqual(a["milestones"][0]["status"],
                         "OPEN_EXIT_EVIDENCE_UNVERIFIED")

    def test_false_task_admission_from_pilot_refused(self):
        p=deepcopy(self.pilot)
        p["qualified_executable_tasks"]=1
        with self.assertRaisesRegex(ValueError,"qualification drift"):
            self.report(pilot=p)

    def test_fake_signed_oracle_or_model_run_from_pilot_refused(self):
        for key,value in (
            ("independent_hidden_oracles_sealed",1),
            ("real_model_runs",1),
            ("confirmed_primary_effect",.1),
            ("matched_real_run_matrix_frozen",True),
            ("pending_admission_checks",15),
        ):
            p=deepcopy(self.pilot)
            p[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                self.report(pilot=p)

    def test_fake_confirmatory_results_flags_refused(self):
        for key,value in (
            ("results_measured",True),("external_code_executions",1),
            ("runner_isolated_and_attested",True),
            ("model_revisions_frozen",True),
            ("policy_implementations_faithfully_reproduced",True),
            ("independent_oracles_sealed",True),
            ("seeds_frozen",True),
            ("final_budget_caps_frozen",True),
            ("deadline","2027-02-01"),
        ):
            p=deepcopy(self.protocol)
            p[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(
                    ValueError,"cannot report promoted"):
                self.report(protocol=p)

    def test_silent_added_policy_or_changed_primary_contrast_refused(self):
        p=deepcopy(self.protocol)
        p["policy_ids"].append("secret_free_oracle")
        with self.assertRaisesRegex(ValueError,"protocol drift"):
            self.report(protocol=p)
        p=deepcopy(self.protocol)
        p["primary_treatment"]="no_uncertainty_search"
        with self.assertRaisesRegex(ValueError,"protocol drift"):
            self.report(protocol=p)

    def test_fake_model_checkpoint_or_execution_refused(self):
        for field,value in (
            ("checkpoint_revision","0"*40),
            ("tokenizer_revision","0"*40),
            ("inference_execution_status","COMPLETED_AND_AUDITED"),
            ("independently_verified_task_runs",1),
        ):
            models=deepcopy(self.models)
            models["models"][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                self.report(selected=models)

    def test_forged_historical_dataset_admission_refused(self):
        m=deepcopy(self.metadata)
        m["independently_approved_executable_tasks"]=1
        with self.assertRaisesRegex(ValueError,"metadata counter"):
            self.report(metadata=m)
        gates=deepcopy(self.gates)
        gates["source_data"]["qualified_executable_tasks"]=1
        with self.assertRaisesRegex(ValueError,"planning register"):
            self.report(gate_register=gates)

    def test_ten_milestone_roster_drift_refused(self):
        for mutate in (
            lambda l:l.pop(),
            lambda l:l.append(deepcopy(l[0])),
            lambda l:l.__setitem__(0,{**l[0],"id":"unregistered-task"}),
        ):
            g=deepcopy(self.gates)
            mutate(g["next_work"])
            with self.assertRaisesRegex(ValueError,"roster drift"):
                self.report(gate_register=g)

    def test_cycle_in_dependency_schedule_refused(self):
        # Local temporary patch, never touch the registered protocol.
        with patch.dict(cp.DEPENDS,{"P0-1":("P2-10",)}):
            with self.assertRaisesRegex(ValueError,"cyclic"):
                cp._dependencies()

    def test_unknown_dependency_refused(self):
        with patch.dict(cp.DEPENDS,{"P1-7":("DOES_NOT_EXIST",)}):
            with self.assertRaisesRegex(ValueError,"unknown"):
                cp._dependencies()

    def test_missing_reference_component_fails_closed(self):
        with patch.dict(cp.REFERENCE_FILES,{"P0-1":("not/a/real/module.py",)}):
            with self.assertRaisesRegex(ValueError,"scaffolding file missing"):
                self.report()

    def test_deterministic_source_digests_and_no_oracle_leaks(self):
        a=self.report()
        b=self.report()
        self.assertEqual(json.dumps(a,sort_keys=True),
                         json.dumps(b,sort_keys=True))
        for p,digest in a["source_record_sha256"].items():
            expected=sha256((self.root/p).read_bytes()).hexdigest()
            self.assertEqual(digest,expected)
        s=json.dumps(a)
        self.assertNotIn("oracle_passed",s)
        self.assertNotIn("gold_output",s)
        self.assertNotIn("reviewer_identity",s)
        self.assertNotIn("reviewer_note",s)

    def test_markdown_avoids_invented_percentage_and_shows_all_issues(self):
        text=cp.critical_path_markdown(self.report())
        self.assertIn("10 of 10",text)
        self.assertIn("16/16",text)
        self.assertIn("P0-1",text)
        self.assertIn("P2-10",text)
        self.assertIn("N/A",text)
        self.assertIn("not a",text.lower())
        self.assertNotIn("100% complete",text)
        for issue in (2,3,4,5,6,7):
            self.assertIn(f"/issues/{issue}",text)

    def test_fabricated_primary_effect_cannot_render_as_markdown(self):
        r=deepcopy(self.report())
        r["scientific_measurement"]["measured_primary_effect"]=.14
        with self.assertRaisesRegex(ValueError,"prospective"):
            cp.critical_path_markdown(r)
        r=deepcopy(self.report())
        r["milestone_accounting"]["overall_percent_complete"]=.9
        with self.assertRaisesRegex(ValueError,"prospective"):
            cp.critical_path_markdown(r)

    def test_real_cli_exports_public_auditable_json_markdown_receipt(self):
        with TemporaryDirectory() as directory:
            out=export_critical_path(Path(directory))
            self.assertEqual(out["qualified_executable_tasks"],0)
            self.assertIsNone(out["overall_percent_complete"])
            names=set(p.name for p in Path(directory).iterdir())
            self.assertEqual(names,{
                "CRITICAL_PATH_STATUS.json","REMAINING_WORK.md",
                "CRITICAL_PATH_INTEGRITY.json",
            })
            integrity=json.loads(
                (Path(directory)/"CRITICAL_PATH_INTEGRITY.json").read_text())
            self.assertTrue(integrity["unqualified_experiment"])
            for name,digest in integrity["files_sha256"].items():
                self.assertEqual(
                    sha256((Path(directory)/name).read_bytes()).hexdigest(),digest)
            stored=json.loads((Path(directory)/"CRITICAL_PATH_STATUS.json").read_text())
            self.assertEqual(stored["milestone_accounting"]
                             ["still_without_full_exit_evidence"],10)
            self.assertNotIn("private reviewer",str(stored).lower())

    def test_require_empirical_ready_cli_fails_status_2(self):
        with TemporaryDirectory() as directory,redirect_stdout(io.StringIO()):
            status=cli(["--output-dir",directory,
                        "--require-empirical-ready"])
            self.assertEqual(status,2)
            self.assertTrue((Path(directory)/"REMAINING_WORK.md").exists())


if __name__=="__main__":
    unittest.main()
