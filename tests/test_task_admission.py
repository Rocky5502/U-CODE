"""U-CODE admission gates: real PR metadata, adversarial nonpromotion tests.

No external repository code is run or imported. The two real cases remain
preexperimental dossiers irrespective of roots' MIT license metadata.
"""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.check_task_admission import (
    DEFAULT_DOSSIERS, validate_prospective_dossiers,
)
from scripts.summarize_audit import load_manifest, load_records
from ucode.task_admission import (
    GateRecord, TaskAdmissionDossier, REQUIRED_GATES,
    assess_dossier, dossier_sha256, parse_dossier,
    validate_dossier_against_metadata,
)


class TaskAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest("data/discovery/agent_pr_candidates_120.csv")
        cls.records = load_records("data/audits/2026-10-24", cls.manifest)
        cls.by_id = {int(r["candidate_id"]): r for r in cls.records}
        cls.original = [json.loads(x) for x in Path(
            DEFAULT_DOSSIERS).read_text(encoding="utf-8").splitlines() if x]
        cls.dossiers = [parse_dossier(x) for x in cls.original]

    def test_both_actual_candidates_have_all_eight_open_gates(self):
        self.assertEqual({x.candidate_id for x in self.dossiers}, {43, 104})
        for obj in self.dossiers:
            result = assess_dossier(obj)
            self.assertEqual(result.stage, "NEEDS_EVIDENCE")
            self.assertEqual(set(result.open_gates), set(REQUIRED_GATES))
            self.assertFalse(result.eligible_for_experiment)
            self.assertTrue(result.requires_independent_adjudication)

    def test_manifest_and_metadata_bind_real_pr_ids_and_shas(self):
        for obj in self.dossiers:
            validate_dossier_against_metadata(
                obj, self.by_id[obj.candidate_id], self.manifest)

    def test_dossier_batch_review_is_deterministic(self):
        one = validate_prospective_dossiers(self.records, self.manifest)
        two = validate_prospective_dossiers(self.records, self.manifest)
        self.assertEqual(one, two)
        self.assertEqual([x["candidate_id"] for x in one], [43, 104])
        self.assertTrue(all(not x["eligible_for_experiment"] for x in one))
        self.assertTrue(all(len(x["dossier_sha256"]) == 64 for x in one))

    def test_metadata_only_sha_is_insufficient_to_pass_prefixed_snapshot(self):
        obj = self.dossiers[0]
        self.assertEqual(obj.gates[0].status, "PENDING")
        self.assertTrue(obj.base_sha and obj.head_sha)
        self.assertIn("immutable_prefixed_snapshot", assess_dossier(obj).open_gates)

    def test_no_automatic_evaluation_promotion_even_if_all_claims_supplied(self):
        obj = self.dossiers[0]
        claims = tuple(GateRecord(
            gate=k, status="EVIDENCE_PRESENT_NOT_ATTESTED",
            evidence_refs=("sha256:external-unverified-artifact",),
            evidence_sha256="a"*64, reviewer="manual-reviewer",
            reviewer_role="rights-oracle-reviewer",
        ) for k in REQUIRED_GATES)
        ready = replace(obj, gates=claims)
        report = assess_dossier(ready)
        self.assertEqual(report.stage, "EXTERNAL_ADJUDICATION_REQUIRED")
        self.assertFalse(report.eligible_for_experiment)
        self.assertTrue(report.requires_independent_adjudication)

    def test_gate_claim_requires_artifact_hash_and_reviewer(self):
        with self.assertRaisesRegex(ValueError, "requires refs"):
            GateRecord(gate=REQUIRED_GATES[0],
                       status="EVIDENCE_PRESENT_NOT_ATTESTED")
        with self.assertRaisesRegex(ValueError, "SHA256"):
            GateRecord(gate=REQUIRED_GATES[0], status="PENDING",
                       evidence_sha256="not-a-digest")

    def test_externally_approved_status_is_not_accepted_from_json(self):
        with self.assertRaisesRegex(ValueError, "status must"):
            GateRecord(gate=REQUIRED_GATES[0], status="APPROVED")
        with self.assertRaisesRegex(ValueError, "cannot declare"):
            replace(self.dossiers[0], evidence_stage="EXPERIMENT_ELIGIBLE")

    def test_required_gates_exactly_once(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            replace(self.dossiers[0],
                    gates=self.dossiers[0].gates[:-1])
        with self.assertRaisesRegex(ValueError, "exactly one"):
            replace(self.dossiers[0],
                    gates=self.dossiers[0].gates[:-1]+self.dossiers[0].gates[:1])

    def test_pr_lineage_change_is_rejected(self):
        obj = self.dossiers[0]
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            validate_dossier_against_metadata(
                replace(obj, base_sha="a"*40),
                self.by_id[obj.candidate_id], self.manifest)

    def test_pr_identity_change_is_rejected(self):
        obj = self.dossiers[0]
        with self.assertRaisesRegex(ValueError, "PR URL"):
            replace(obj, pr_url="https://github.com/other/project/pull/77")

    def test_external_source_path_not_in_changed_files_is_rejected(self):
        obj = self.dossiers[0]
        with self.assertRaisesRegex(ValueError, "absent"):
            validate_dossier_against_metadata(
                replace(obj, changed_production_paths=("src/fake/new.py",)),
                self.by_id[obj.candidate_id], self.manifest)

    def test_path_escape_rejected_prior_to_sandbox(self):
        obj = self.dossiers[0]
        for path in ("../secret.py", "/var/run/secret", "C:/Windows/file.go",
                     "src/../escape.rb", r"src\\evil.py"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                replace(obj, changed_production_paths=(path,))

    def test_duplicate_dossier_rejected(self):
        with TemporaryDirectory() as td:
            p = Path(td)/"dupes.jsonl"
            p.write_text(json.dumps(self.original[0])+"\n"+
                         json.dumps(self.original[0])+"\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate dossier"):
                validate_prospective_dossiers(self.records, self.manifest, p)

    def test_digest_changes_when_dossier_evidence_changes(self):
        original = self.original[0]
        changed = deepcopy(original)
        changed["narrative"] += " extra non-test text"
        self.assertNotEqual(dossier_sha256(original), dossier_sha256(changed))

    def test_failed_gate_prevents_even_manual_review_ready(self):
        obj = self.dossiers[0]
        failure = GateRecord(gate="sandbox_isolation", status="FAILED",
                             note="Network-off isolation not available")
        new = replace(obj, gates=tuple(failure if g.gate==failure.gate else g
                                       for g in obj.gates))
        result = assess_dossier(new)
        self.assertEqual(result.stage, "REJECT_FOR_PILOT")
        self.assertFalse(result.eligible_for_experiment)


if __name__ == "__main__":
    unittest.main()
