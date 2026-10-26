"""Build cleaned, auditable metadata-only U-CODE dataset from frozen PR ledgers.

Does not clone repositories, read external APIs, execute any source, label
success, or authorize protected model experiments. Reproduction requires
only the project's existing 120-PR CSV and canonical audited JSONLs.
"""
import argparse
from hashlib import sha256
from pathlib import Path
import json

from scripts.summarize_audit import load_manifest, load_records
from ucode.dataset_curation import LANGUAGES, build_dataset, write_dataset

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/discovery/agent_pr_candidates_120.csv"
AUDIT_DIR = ROOT / "data/audits/2026-10-24"
DEFAULT_OUT = ROOT / "dist/datasets/ucode_pr_metadata_v1"


def run(*, manifest_path=SOURCE, audit_dir=AUDIT_DIR, output_dir=DEFAULT_OUT,
        review_limit=12):
    path = Path(manifest_path)
    raw = path.read_bytes()
    rows = load_manifest(path)
    audit = load_records(audit_dir, rows)
    if len(rows) != 120:
        raise ValueError("frozen discovery manifest expected 120 PR links")
    if len(audit) != 120:
        raise ValueError("all 120 canonical audit entries required")
    data = build_dataset(rows, audit, sha256(raw).hexdigest(), review_limit)
    if len(data.language_summary) != len(LANGUAGES):
        raise ValueError("all 12 original search-language strata required")
    hashes = write_dataset(data, output_dir)
    return {"stage": "METADATA_ONLY_NO_EXECUTABLE_TASK_ADMISSION",
            "output_dir": str(output_dir), "files_sha256": hashes,
            **data.report}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=SOURCE)
    p.add_argument("--audit-dir", type=Path, default=AUDIT_DIR)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--review-limit", type=int, default=12)
    args = p.parse_args(argv)
    result = run(manifest_path=args.manifest,
                 audit_dir=args.audit_dir,
                 output_dir=args.output_dir,
                 review_limit=args.review_limit)
    print(json.dumps(result, sort_keys=True, indent=2))
    print("NO TASKS ADMITTED. NO MODEL OR EXTERNAL CODE EXECUTED.")


if __name__ == "__main__":
    main()
