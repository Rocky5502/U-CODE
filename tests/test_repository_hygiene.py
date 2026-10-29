"""Guard required research files and avoid accidentally tracked sensitive assets."""
import unittest
from scripts.audit_repository_hygiene import audit_tracked_paths, _REQUIRED

class RepositoryHygieneTests(unittest.TestCase):
    def sample(self):
        return sorted(_REQUIRED) + ["src/ucode/voi.py", "data/curated/2026-10-27/discovery_frame_120_NOT_EXECUTABLE.csv"]

    def test_required_project_surface_and_source_data_are_allowed(self):
        result = audit_tracked_paths(self.sample())
        self.assertEqual(result["missing_required_paths"], 0)
        self.assertEqual(result["forbidden_paths"], 0)
        self.assertIn("NOT_SECRET_SCANNER", result["security_claim"])

    def test_unvetted_files_cannot_be_committed(self):
        bad = [
            "data/raw/repo.zip", "data/derived/private.json",
            "data/cache/local.sqlite", "models/weights.bin",
            "checkpoints/model.tar", "runs/traces.json",
            "outputs/result.csv", "artifacts/private.zip",
            ".env", ".env.production", ".venv/bin/python",
            "secrets.pem", "id_rsa", "weights.gguf",
            "model.safetensors", "eval.private.key",
            "task-oracle.parquet",
        ]
        for path in bad:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "forbidden_paths"):
                audit_tracked_paths(self.sample() + [path])

    def test_ci_source_and_secret_template_allowed(self):
        report = audit_tracked_paths(self.sample() + [".env.example", ".github/workflows/ci.yml"])
        self.assertEqual(report["forbidden_paths"], 0)

    def test_missing_required_security_policy_rejected(self):
        x = [p for p in self.sample() if p != "SECURITY.md"]
        with self.assertRaisesRegex(ValueError, "missing_required"):
            audit_tracked_paths(x)

    def test_duplicate_invalid_and_path_traversal_rejected(self):
        for path in ("../secret", "src/../secrets", "/etc/passwd", "src\\secrets"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "unsafe"):
                audit_tracked_paths(self.sample() + [path])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit_tracked_paths(self.sample() + ["README.md"])

if __name__ == "__main__":
    unittest.main()
