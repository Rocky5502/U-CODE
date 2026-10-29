"""Offline tracked-file allowlist check; NOT a comprehensive secret scanner.

The Git index lists committed file paths, not downloaded data, runtime
processes, licenses, content hashes or live system security. Keep this audit
independent of executing third-party repository code.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import PurePosixPath

_FORBIDDEN_PREFIXES = (
    "data/raw/", "data/derived/", "data/cache/", "models/", "checkpoints/",
    "outputs/", "runs/", "artifacts/", "hf_cache/", "huggingface_cache/",
    ".venv/", "venv/",
)
_FORBIDDEN_NAMES = frozenset((".env", "id_rsa", "id_ed25519"))
_FORBIDDEN_SUFFIXES = frozenset((
    ".safetensors", ".gguf", ".pt", ".pth", ".ckpt", ".onnx",
    ".parquet", ".arrow", ".h5", ".hdf5", ".pickle", ".pkl",
    ".pem", ".key",
))
_REQUIRED = frozenset((
    "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "README.md",
    "requirements.txt", "requirements-dev.txt", "pyproject.toml",
    "docs/MODELS.md", "docs/DATASETS.md", "docs/LOCAL_EXPERIMENTS.md",
    "configs/local_experiment_preflight_2026-10-29.json",
))


def audit_tracked_paths(paths: list[str]) -> dict:
    if type(paths) is not list or not paths:
        raise ValueError("git index path inventory must be nonempty")
    seen = set()
    forbidden = []
    for path in paths:
        if type(path) is not str or not path or path in seen:
            raise ValueError("invalid or duplicate tracked file path")
        seen.add(path)
        if (path.startswith("/") or "\\" in path
                or any(part in ("..", ".") for part in path.split("/"))):
            raise ValueError("unsafe tracked path")
        pure = PurePosixPath(path)
        name = pure.name.lower()
        if (any(path.startswith(prefix) for prefix in _FORBIDDEN_PREFIXES)
                or name in _FORBIDDEN_NAMES
                or (name.startswith(".env.") and name != ".env.example")
                or pure.suffix.lower() in _FORBIDDEN_SUFFIXES):
            forbidden.append(path)
    missing = sorted(_REQUIRED - seen)
    if forbidden or missing:
        raise ValueError(
            "tracked repository hygiene failed: forbidden_paths="
            + repr(sorted(forbidden)) + " missing_required=" + repr(missing)
        )
    return {
        "status": "TRACKED_PATHS_PASS_STATIC_FILTER",
        "tracked_paths": len(seen),
        "forbidden_paths": 0,
        "missing_required_paths": 0,
        "security_claim": "FILENAME_SCREEN_ONLY_NOT_SECRET_SCANNER_OR_SANDBOX_ATTESTATION",
    }


def main() -> None:
    result = subprocess.run(
        ["git", "ls-files", "-z"], check=True,
        capture_output=True, timeout=20,
    )
    paths = [p.decode("utf-8") for p in result.stdout.split(b"\0") if p]
    print(json.dumps(audit_tracked_paths(paths), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
