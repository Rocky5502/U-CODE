"""Adversarial first-party tests: manifest binding is not independent attestation."""
from dataclasses import replace
import unittest

from ucode.attrition_bounds import paired_effect_attrition_bounds
from ucode.experiment_contract import (
    EvaluatorVerdict, FrozenStudy, PolicyRunReceipt,
    audit_confirmatory_run_matrix,
)
from ucode.frozen_oracle_contract import FrozenOracleManifest
from ucode.postterminal_accounting import postterminal_contrast
from ucode.vector_policy import ResourceVector as RV


class DeclaredFrozenOracleManifestTests(unittest.TestCase):
    def setUp(self):
        cap = RV(tokens=10, test_calls=2, gpu_seconds=1,
                 cpu_seconds=2, wall_seconds=4)
        self.study = FrozenStudy(
            (("task-release", "lineage-A"), ("task-abstain", "lineage-B")),
            ("synthetic-model",), ("treatment", "control"),
            (11,), (("budget", cap),),
        )
        rows, verdicts = [], []
        for task_id, group in self.study.task_lineages:
            for policy in self.study.policies:
                released = task_id == "task-release"
                patch = (("c" if policy == "treatment" else "d")*64
                         if released else None)
                rows.append(PolicyRunReceipt(
                    task_id, group, "synthetic-model", policy, 11, "budget",
                    "a"*40, "b"*40, "1"*64, "2"*64,
                    RV(tokens=2, test_calls=1),
                    "release" if released else "abstain",
                    patch, "3"*64,
                ))
                if released:
                    verdicts.append(EvaluatorVerdict(
                        task_id, "synthetic-model", policy, 11, "budget",
                        patch, "4"*64, policy == "treatment", "5"*64,
                    ))
        self.rows, self.verdicts = tuple(rows), tuple(verdicts)
        self.manifest = FrozenOracleManifest((
            ("task-release", "4"*64),
            ("task-abstain", "6"*64),
        ))

    def audit(self, manifest=None, verdicts=None, rows=None):
        return audit_confirmatory_run_matrix(
            self.study, self.rows if rows is None else rows,
            self.verdicts if verdicts is None else verdicts,
            frozen_oracles=manifest,
        )

    def test_all_task_declarations_match_and_admission_not_implied(self):
        report = self.audit(self.manifest)
        self.assertEqual(report.verified_oracle_receipts, 2)
        self.assertTrue(report.declared_frozen_oracle_bindings_match)
        self.assertFalse(report.independently_authenticated_oracles)
        self.assertEqual(len(report.outcomes), 4)

    def test_legacy_structural_checks_do_not_claim_precommitment(self):
        report = self.audit()
        self.assertFalse(report.declared_frozen_oracle_bindings_match)
        self.assertFalse(report.independently_authenticated_oracles)

    def test_consistent_posthoc_oracle_swap_requires_precommitted_manifest(self):
        changed = tuple(replace(v, oracle_artifact_sha256="9"*64)
                        for v in self.verdicts)
        # Same erroneous oracle in every released verdict is self-consistent
        # and hence passes without the separately frozen declaration.
        self.assertFalse(
            self.audit(verdicts=changed).declared_frozen_oracle_bindings_match)
        with self.assertRaisesRegex(ValueError, "declared frozen task oracle"):
            self.audit(self.manifest, verdicts=changed)

    def test_all_abstain_task_cannot_vanish_from_frozen_registry(self):
        missing = FrozenOracleManifest((("task-release", "4"*64),))
        with self.assertRaisesRegex(ValueError, "every assigned task"):
            self.audit(missing)
        extra = FrozenOracleManifest((
            ("task-release", "4"*64), ("task-abstain", "6"*64),
            ("invented-task", "7"*64),
        ))
        with self.assertRaisesRegex(ValueError, "every assigned task"):
            self.audit(extra)

    def test_all_abstain_still_validates_registry_completeness(self):
        rows = tuple(replace(r, termination="abstain", patch_sha256=None)
                     for r in self.rows)
        audit = self.audit(self.manifest, verdicts=(), rows=rows)
        self.assertTrue(audit.declared_frozen_oracle_bindings_match)
        self.assertEqual(audit.verified_oracle_receipts, 0)
        self.assertEqual(len(audit.outcomes), 4)

    def test_unknown_duplicate_invalid_and_mutable_manifest_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            FrozenOracleManifest((
                ("task-release", "4"*64), ("task-release", "6"*64),
            ))
        with self.assertRaisesRegex(ValueError, "SHA256"):
            FrozenOracleManifest((("task-release", "a"*40),))
        with self.assertRaisesRegex(ValueError, "tuple"):
            FrozenOracleManifest([("task-release", "4"*64)])
        with self.assertRaisesRegex(ValueError, "immutable task/digest pair"):
            FrozenOracleManifest((["task-release", "4"*64],))
        with self.assertRaisesRegex(ValueError, "authenticity"):
            replace(self.manifest, stage="INDEPENDENTLY_VERIFIED")
        with self.assertRaisesRegex(TypeError, "typed declared frozen"):
            self.audit({"task-release": "4"*64})

    def test_postterminal_effect_respects_frozen_manifest(self):
        out = postterminal_contrast(
            self.study, self.rows, self.verdicts, "treatment", "control",
            frozen_oracles=self.manifest, bootstrap_samples=20)
        self.assertEqual(out.assigned_pairs, 2)
        self.assertFalse(out.real_trial_approved)
        changed = replace(self.manifest, task_oracles=(
            ("task-release", "9"*64), ("task-abstain", "6"*64),
        ))
        with self.assertRaisesRegex(ValueError, "declared frozen task oracle"):
            postterminal_contrast(
                self.study, self.rows, self.verdicts, "treatment", "control",
                frozen_oracles=changed, bootstrap_samples=20)

    def test_attrition_bounds_respect_frozen_manifest(self):
        bounds = paired_effect_attrition_bounds(
            self.study, self.rows, self.verdicts, "treatment", "control",
            frozen_oracles=self.manifest)
        self.assertEqual(bounds.assigned_pairs, 2)
        changed = FrozenOracleManifest((
            ("task-release", "9"*64), ("task-abstain", "6"*64),
        ))
        with self.assertRaisesRegex(ValueError, "declared frozen task oracle"):
            paired_effect_attrition_bounds(
                self.study, self.rows, self.verdicts, "treatment", "control",
                frozen_oracles=changed)


if __name__ == "__main__":
    unittest.main()
