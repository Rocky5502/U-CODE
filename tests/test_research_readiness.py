"""Research-status and endpoint semantics; NO observed coding-agent results."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.build_clean_pr_dataset import ROOT
from scripts.export_research_readiness import export_readiness
from ucode.research_readiness import (
    METRIC_DEFINITIONS,ReadinessSnapshot,build_readiness_snapshot,readiness_markdown,
)


class ResearchReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen=json.loads((ROOT/"data/curated/2026-10-27/frozen_cleaning_summary.json").read_text())
        cls.gates=json.loads((ROOT/"configs/ucode_work_remaining_gates_2026-10-27.json").read_text())
        cls.protocol=json.loads((ROOT/"configs/confirmatory_sbse_protocol_2026-10-25.json").read_text())
        cls.verified={
            "semantic_audit":{
                "pr_discovery_rows":120,
                "metadata_retrieved":119,
                "production_source_path_leads":62,
                "shortlisted_manual_review":12,
                "approved_executable_tasks":0,
            },
        }

    def snap(self,f=None,g=None,p=None,v=None,n=13):
        return build_readiness_snapshot(
            self.frozen if f is None else f,
            self.gates if g is None else g,
            self.protocol if p is None else p,
            self.verified if v is None else v,n,
        )

    def test_all_six_metrics_are_explicitly_unobserved(self):
        s=self.snap().data
        self.assertEqual(len(s["metric_dictionary"]),6)
        self.assertEqual(set(s["observed_metric_values"]),
                         set(x["id"] for x in METRIC_DEFINITIONS))
        self.assertTrue(all(x is None for x in s["observed_metric_values"].values()))
        self.assertIsNone(s["observed_denominator"])
        self.assertEqual(s["metadata"]["records"],120)
        self.assertEqual(s["metadata"]["production_source_path_leads"],62)
        self.assertEqual(s["metadata"]["candidate_public_dataset_sources"],13)
        self.assertEqual(s["confirmatory_study"]["planned_model_names"],6)
        self.assertEqual(s["confirmatory_study"]["planned_policy_slots"],8)

    def test_wrong_release_risk_undefined_at_no_releases(self):
        m=next(x for x in METRIC_DEFINITIONS if x["id"]=="wrong_release_risk")
        self.assertIn("null (not zero",m["zero_denominator"])
        self.assertTrue(m["oracle_required"])

    def test_itt_requires_all_assigned_cells(self):
        m=next(x for x in METRIC_DEFINITIONS
               if x["id"]=="verified_full_task_success_itt")
        self.assertIn("all assigned cells",m["denominator"])
        self.assertIn("abstain",m["denominator"])

    def test_reporting_text_cannot_pretend_real_performance(self):
        report=readiness_markdown(self.snap())
        self.assertIn("no verified empirical",report.lower())
        self.assertIn("N/A",report)
        self.assertIn("not zero",report)
        self.assertIn("twelve query-language",report)

    def test_drifted_frozen_dataset_numbers_rejected(self):
        f=deepcopy(self.frozen)
        f["metadata_retrieved"]=120
        with self.assertRaisesRegex(ValueError,"discovery denominator"):
            self.snap(f=f)

    def test_drifted_remaining_work_status_rejected(self):
        g=deepcopy(self.gates)
        g["source_data"]["qualified_executable_tasks"]=1
        with self.assertRaisesRegex(ValueError,"dataset gate disagrees"):
            self.snap(g=g)

    def test_drifted_semantic_report_rejected(self):
        v=deepcopy(self.verified)
        v["semantic_audit"]["shortlisted_manual_review"]=13
        with self.assertRaisesRegex(ValueError,"semantic snapshot"):
            self.snap(v=v)

    def test_missing_semantics_rejected(self):
        with self.assertRaisesRegex(ValueError,"cross-file semantic"):
            self.snap(v={})

    def test_falsified_completed_experiment_rejected(self):
        p=deepcopy(self.protocol)
        p["results_measured"]=True
        with self.assertRaisesRegex(ValueError,"incorrectly promoted"):
            self.snap(p=p)

    def test_promoted_overleaf_pdf_status_rejected(self):
        g=deepcopy(self.gates)
        g["paper"]["actual_springer_pdf_compiled_and_inspected"]=True
        with self.assertRaisesRegex(ValueError,"manuscript report"):
            self.snap(g=g)

    def test_extra_registered_control_not_silently_appended(self):
        p=deepcopy(self.protocol)
        p["policy_ids"].append("free_extra_oracle")
        with self.assertRaisesRegex(ValueError,"roster drift"):
            self.snap(p=p)

    def test_unauthenticated_dataset_source_disallowed(self):
        with self.assertRaisesRegex(ValueError,"candidate registry"):
            self.snap(n=0)

    def test_none_is_not_zero_in_observation_gate(self):
        d=deepcopy(self.snap().data)
        d["observed_metric_values"]["wrong_release_risk"]=0
        with self.assertRaisesRegex(ValueError,"no empirical values"):
            readiness_markdown(ReadinessSnapshot(d))

    def test_real_export_rebuilds_actual_120_record_metadata_release(self):
        with tempfile.TemporaryDirectory() as temp:
            status=export_readiness(Path(temp))
            self.assertEqual(status["metadata_discovery_records"],120)
            self.assertEqual(status["experimentally_qualified_tasks"],0)
            json_path=Path(temp)/"research_readiness.json"
            md_path=Path(temp)/"RESEARCH_METRICS_AND_STATUS.md"
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            d=json.loads(json_path.read_text())
            self.assertEqual(d["observed_metric_values"]["wrong_release_risk"],None)
            self.assertIn("Dataset integrity",md_path.read_text())


if __name__=="__main__":
    unittest.main()
