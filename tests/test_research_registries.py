"""First-party candidate-inventory guards, without remote model downloads."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_research_registries import (
    DATASETS, MODELS, REQUIRED_DATA_COLUMNS, validate_registries,
)


class ResearchRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.model_path = root / "models.json"
        self.dataset_path = root / "sources.csv"
        self.models = json.loads(MODELS.read_text(encoding="utf-8"))
        with DATASETS.open(newline="", encoding="utf-8") as s:
            self.datasets = list(csv.DictReader(s))

    def save(self):
        self.model_path.write_text(json.dumps(self.models), encoding="utf-8")
        with self.dataset_path.open("w", encoding="utf-8", newline="") as s:
            writer = csv.DictWriter(s, fieldnames=sorted(REQUIRED_DATA_COLUMNS))
            writer.writeheader()
            writer.writerows(self.datasets)
        return self.model_path, self.dataset_path

    def test_actual_registry_has_six_unfrozen_models_and_thirteen_leads(self):
        self.assertEqual(validate_registries(), {"models": 6, "datasets": 13})

    def test_duplicate_model_fails(self):
        self.models["models"][1]["id"] = self.models["models"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_registries(*self.save())

    def test_no_accidental_model_license_approval(self):
        self.models["models"][0]["rights_approved"] = True
        with self.assertRaisesRegex(ValueError, "promoted"):
            validate_registries(*self.save())

    def test_no_unreviewed_mutable_model_revision(self):
        self.models["models"][0]["model_revision"] = "main"
        with self.assertRaisesRegex(ValueError, "unexpectedly pinned"):
            validate_registries(*self.save())

    def test_no_fake_executable_task_label(self):
        self.datasets[0]["local_execution"] = "verified"
        with self.assertRaisesRegex(ValueError, "disguised"):
            validate_registries(*self.save())

    def test_invalid_model_source_url(self):
        self.models["models"][0]["url"] = "http://not-trusted.example"
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            validate_registries(*self.save())

    def test_invalid_dataset_cohort(self):
        self.datasets[0]["distinct_cohort"] = "Everything_Pooled"
        with self.assertRaisesRegex(ValueError, "cohort"):
            validate_registries(*self.save())


if __name__ == "__main__":
    unittest.main()
