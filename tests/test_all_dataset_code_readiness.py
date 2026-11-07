"""Synthetic adversarial integrity tests for all 13 frozen dataset sources.

No third-party corpus, model, executable, private reviewer data or oracle is
accessed; CI only validates known first-party metadata and blocked readiness.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from contextlib import redirect_stdout
import io
import json
import unittest

from scripts.audit_all_dataset_readiness import export_all_dataset_readiness,main as cli
from scripts.audit_dataset_cohort_crosswalk import read_csv,RAW,CLEAN,SOURCES,LEGACY,SUMMARY
from ucode import dataset_code_readiness as audit


class AllSourceCodeReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.external=read_csv(SOURCES)
        cls.raw=read_csv(RAW)
        cls.curated=read_csv(CLEAN)
        cls.legacy_sources=read_csv(LEGACY)
        cls.summary=json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.protocol=audit._json(audit.ROOT,audit.REGISTRY_PATH)
        cls.models=audit._json(audit.ROOT,audit.MODEL_PATH)
        cls.experiment=audit._json(audit.ROOT,audit.LEGACY_PATH)
        cls.pilot=audit.build_pilot_preflight()

    def check(self,**changes):
        args={
            "external":self.external,
            "raw":self.raw,
            "curated":self.curated,
            "legacy_sources":self.legacy_sources,
            "summary":self.summary,
            "protocol":self.protocol,
            "selected":self.models,
            "legacy_matrix":self.experiment,
            "pilot":self.pilot,
        }
        args.update(changes)
        return audit.audit_dataset_code_readiness(**args)

    def test_all_thirteen_sources_categorized_without_merging_grains(self):
        r=self.check()
        self.assertEqual(r["dataset_catalog_count"],13)
        self.assertEqual([x["dataset"] for x in r["per_dataset"]],list(audit.SOURCE_NAMES))
        self.assertEqual(r["cohort_counts"],{
            "Attribution_only":3,
            "Auxiliary_training":3,
            "Controlled_generation":4,
            "Efficiency_secondary":1,
            "Naturalistic":2,
        })
        self.assertEqual(len(set(r["per_dataset"][i]["candidate_role"]
                             for i in range(13))),5)

    def test_not_one_external_source_is_admitted_or_auto_executed(self):
        r=self.check()
        self.assertEqual(r["dataset_snapshot_count_independently_verified"],0)
        self.assertEqual(r["dataset_rights_filelevel_approved_count"],0)
        self.assertEqual(r["independent_oracle_replay_count"],0)
        for item in r["per_dataset"]:
            self.assertFalse(item["local_data_snapshot_proven"])
            self.assertFalse(item["independent_file_reuse_rights_approved"])
            self.assertFalse(item["independent_oracle_reproduced"])
            self.assertFalse(item["physical_runner_and_meters_attested"])
            self.assertFalse(item["can_supply_primary_confirmatory_effect"])
            self.assertEqual(item["qualified_executable_task_count"],0)

    def test_curated_public_metadata_proven_but_not_runnable(self):
        r=self.check()
        self.assertEqual(r["public_discovery_metadata"]["pr_links"],120)
        self.assertEqual(r["public_discovery_metadata"]["retrieved_pr_metadata"],119)
        self.assertEqual(r["public_discovery_metadata"]["production_path_leads"],62)
        self.assertEqual(r["public_discovery_metadata"]["shortlisted_reviewer_packets"],12)
        self.assertTrue(r["public_discovery_metadata"]["metadata_identity_reconciliation_passed"])
        self.assertEqual(r["public_discovery_metadata"]["qualified_executable_tasks"],0)

    def test_legacy_old_seven_arm_four_resource_config_is_not_authority(self):
        r=self.check()
        w=r["legacy_experiment_matrix_warning"]
        self.assertEqual((w["old_policy_arm_count"],w["old_resource_dimensions"]),(7,4))
        self.assertEqual((w["authoritative_policy_arm_count"],w["authoritative_resource_dimensions"]),(8,5))
        self.assertTrue(w["policy_names_mismatched"])
        self.assertTrue(w["never_use_for_confirmatory_experiment"])
        p=r["confirmatory_design"]
        self.assertEqual(p["primary_treatment"],"ucode_conditional_bes")
        self.assertEqual(p["primary_comparator"],"no_uncertainty_search")
        self.assertEqual(len(p["resource_dimensions"]),5)

    def test_primary_contrast_or_policy_silent_change_rejected(self):
        for key,value in (("primary_treatment","random"),
                          ("primary_comparator","fixed_testing"),
                          ("results_measured",True),
                          ("external_code_executions",1),
                          ("runner_isolated_and_attested",True),
                          ("independent_oracles_sealed",True),
                          ("model_revisions_frozen",True)):
            p=deepcopy(self.protocol)
            p[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,"protocol drift"):
                self.check(protocol=p)

    def test_eight_policy_roster_cannot_be_silently_truncated_or_duplicated(self):
        for mutate in (lambda p:p.pop(),lambda p:p.__setitem__(0,p[1])):
            p=deepcopy(self.protocol)
            mutate(p["policy_ids"])
            with self.assertRaisesRegex(ValueError,"protocol drift"):
                self.check(protocol=p)

    def test_no_silent_model_change_or_fake_revision(self):
        models=deepcopy(self.models)
        models["models"][0]["model_id"]="NOT_REGISTERED"
        with self.assertRaisesRegex(ValueError,"crosswalk drift"):
            self.check(selected=models)
        for field,value in (("checkpoint_revision","0"*40),
                            ("tokenizer_revision","a"*40),
                            ("inference_execution_status","COMPLETED_AND_AUDITED"),
                            ("independently_verified_task_runs",1)):
            models=deepcopy(self.models)
            models["models"][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                self.check(selected=models)

    def test_source_catalog_false_execution_promotion_rejected(self):
        ext=deepcopy(self.external)
        ext[3]["local_execution"]="ran_on_GPU_successfully"
        with self.assertRaises(ValueError):
            self.check(external=ext)
        ext=deepcopy(self.external)
        ext[2]["primary_url"]="http://evil.test/source"
        with self.assertRaises(ValueError):
            self.check(external=ext)

    def test_source_catalog_reorder_duplicate_or_missing_fails_closed(self):
        for mutate in (
            lambda e:e.reverse(),
            lambda e:e.pop(),
            lambda e:e.__setitem__(1,deepcopy(e[0])),
        ):
            ext=deepcopy(self.external)
            mutate(ext)
            with self.assertRaises(ValueError):
                self.check(external=ext)

    def test_source_specific_gating_and_license_not_assumed_clear(self):
        r={x["dataset"]:x for x in self.check()["per_dataset"]}
        self.assertEqual(r["SWE-chat"]["source_specific_risk_code"],"GATED_ACCESS_AND_POSSIBLE_PII")
        self.assertEqual(r["CodeMirage"]["source_specific_risk_code"],"RESTRICTIVE_CC_BY_NC_ND")
        self.assertEqual(r["SWE-rebench V2"]["source_specific_risk_code"],"SINGLE_UPSTREAM_TRAIN_SPLIT_AND_GOLD_PATCHES")
        self.assertEqual(r["EffiBench-X"]["catalog_cohort"],"Efficiency_secondary")
        self.assertEqual(r["NextCoderDataset-Conversational"]["catalog_cohort"],"Auxiliary_training")
        self.assertFalse(r["MultiAIGCD"]["local_data_snapshot_proven"])

    def test_two_real_pilot_candidates_still_sixteen_blocked_gates(self):
        r=self.check()
        self.assertEqual(r["pilot"],{
            "source_era_candidates":2,"admission_gates_pending":16,
            "admission_gates_total":16,"qualified_tasks":0,
        })
        for field,bad in (("qualified_executable_tasks",1),
                          ("independent_hidden_oracles_sealed",2),
                          ("real_model_runs",1),
                          ("pending_admission_checks",0),
                          ("confirmed_primary_effect",0.99)):
            p=deepcopy(self.pilot)
            p[field]=bad
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,"pilot evidence"):
                self.check(pilot=p)

    def test_legacy_matrix_promoted_to_executed_is_rejected(self):
        old=deepcopy(self.experiment)
        old["state"]="EXECUTED"
        with self.assertRaisesRegex(ValueError,"legacy experiment sketch"):
            self.check(legacy_matrix=old)
        old=deepcopy(self.experiment)
        old["arms"]=list(self.protocol["policy_ids"])
        old["budget_constraints"]=["a","b","c","d","e"]
        with self.assertRaisesRegex(ValueError,"legacy experiment sketch changed"):
            self.check(legacy_matrix=old)

    def test_duplicate_identity_in_raw_and_unapproved_curated_split_rejected(self):
        raw=deepcopy(self.raw)
        raw[1]["id"]=raw[0]["id"]
        with self.assertRaisesRegex(ValueError,"duplicate raw"):
            self.check(raw=raw)
        curated=deepcopy(self.curated)
        curated[0]["split_status"]="TEST_APPROVED"
        with self.assertRaisesRegex(ValueError,"must not claim"):
            self.check(curated=curated)

    def test_first_party_source_paths_are_checked_not_asserted_real_runnable(self):
        r=self.check()
        code=r["code_readiness"]
        self.assertEqual(code["first_party_component_groups_inspected"],10)
        self.assertEqual(code["source_scaffolds_present"],10)
        self.assertEqual(code["qualified_real_end_to_end_groups"],0)
        for row in code["components"]:
            self.assertTrue(row["files_present"])
            self.assertFalse(row["real_end_to_end_experiment_qualified"])
            self.assertTrue(all((audit.ROOT/p).is_file() for p in row["first_party_files"]))
        with patch.dict(audit.SOURCE_FILE_MAP,{
            "model_readiness":("definitely/missing.py",)}):
            with self.assertRaisesRegex(ValueError,"scaffold"):
                self.check()

    def test_cross_registry_sha256_receipts_are_real_first_party_bytes(self):
        r=self.check()
        for path,actual in r["source_integrity_sha256"].items():
            self.assertEqual(actual,sha256((audit.ROOT/path).read_bytes()).hexdigest())
        self.assertEqual(len(r["source_integrity_sha256"]),5)

    def test_markdown_is_dataset_complete_and_primary_study_not_misleading(self):
        md=audit.readiness_markdown(self.check())
        for dataset in audit.SOURCE_NAMES:
            self.assertIn(dataset,md)
        self.assertIn("16/16",md)
        self.assertIn("7",md)
        self.assertIn("8",md)
        self.assertIn("0",md)
        self.assertIn("no model inference",md.lower())
        self.assertNotIn("100% ready",md.lower())
        r=self.check()
        r["confirmatory_design"]["verified_real_primary_effect"]=.1
        with self.assertRaisesRegex(ValueError,"unverified"):
            audit.readiness_markdown(r)

    def test_report_is_deterministic_without_claiming_live_web_or_disk_scan(self):
        a=self.check()
        b=self.check()
        self.assertEqual(json.dumps(a,sort_keys=True),json.dumps(b,sort_keys=True))
        self.assertTrue(a["disclosures"]["not_a_live_check_of_all_external_hosts"])
        self.assertTrue(a["disclosures"]["not_a_local_data_disk_inventory"])
        self.assertTrue(a["disclosures"]["no_actual_outcome_labels"])

    def test_cli_public_status_and_sha_are_reproducible(self):
        with TemporaryDirectory() as td:
            output=export_all_dataset_readiness(Path(td))
            self.assertEqual(output["external_sources"],13)
            self.assertTrue(output["legacy_experiment_config_incompatible"])
            self.assertEqual(output["qualified_executable_tasks"],0)
            report=json.loads((Path(td)/"ALL_DATASET_READINESS.json").read_text())
            checks=json.loads((Path(td)/"ALL_DATASET_STATUS_SHA256.json").read_text())
            for name,digest in checks["sha256"].items():
                self.assertEqual(sha256((Path(td)/name).read_bytes()).hexdigest(),digest)
            self.assertEqual(len(report["per_dataset"]),13)

    def test_strict_cli_return_2_without_dataset_authorization(self):
        with TemporaryDirectory() as td,redirect_stdout(io.StringIO()):
            self.assertEqual(cli(["--output-dir",td,"--require-runnable"]),2)
            self.assertTrue((Path(td)/"ALL_DATASET_CODE_STATUS.md").exists())

    def test_fake_oracle_result_and_extra_fields_not_exposed_as_data_release(self):
        r=self.check()
        public=json.dumps(r)
        self.assertNotIn("gold_patch",public)
        self.assertNotIn("oracle_passed",public)
        self.assertNotIn("reviewer_private_note",public)
        self.assertIsNone(r["confirmatory_design"]["verified_real_primary_effect"])


if __name__=="__main__":
    unittest.main()
