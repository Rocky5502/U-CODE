"""Opt-in, CPU-only projection of a LOCALLY PINNED SWE-rebench V2 snapshot.

Never downloads datasets or executes Docker/third-party code.
Only 7 safe Parquet columns are read; patches, oracle tests, install
instructions and LLM-generated quality annotations are NOT projected.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from scripts.summarize_audit import load_manifest
from scripts.build_clean_pr_dataset import SOURCE
from ucode.external_dataset_intake import (
    csv_release, read_local_parquet_projected, screen_swe_rebench_v2,
)


def inspect_snapshot(paths, revision: str, output_dir: Path):
    files = tuple(sorted(Path(x) for x in paths))
    if not files or len(set(files)) != len(files):
        raise ValueError("must supply one or more distinct local Parquet files")
    # Source digests before opening/parsing. No network and no task execution.
    provenance = {}
    for p in files:
        if not p.is_file() or p.suffix != ".parquet" or p.is_symlink():
            raise ValueError("normal local .parquet snapshots only")
        h = sha256()
        with p.open("rb") as stream:
            for block in iter(lambda: stream.read(1024*1024), b""):
                h.update(block)
        provenance[p.name] = {"sha256": h.hexdigest(),
                              "bytes": p.stat().st_size}
    if len(provenance) != len(files):
        raise ValueError("duplicate basename of external snapshot shard")
    manifest = load_manifest(SOURCE)
    result = screen_swe_rebench_v2(
        read_local_parquet_projected(files),
        revision=revision,
        existing_discovery_repositories=[x["repository"]
                                         for x in manifest.values()])
    if result.report["rows_scanned_in_LOCAL_snapshot"] == 0:
        raise ValueError("empty source snapshot")
    output_dir.mkdir(parents=True, exist_ok=True)
    written = {
        "external_candidates_METADATA_ONLY.csv": csv_release(result),
        "excluded_records.json": json.dumps(result.exclusions, indent=2)+"\n",
        "intake_report.json": json.dumps(result.report, indent=2)+"\n",
        "source_parquet_sha256.json": json.dumps(
            {"external_snapshot_shards": provenance,
             "dataset_revision": revision,
             "code_execution": False,
             "task_admission": False}, indent=2)+"\n",
    }
    for name, content in written.items():
        (output_dir/name).write_text(content, encoding="utf-8")
    return {**result.report,
            "written_files": sorted(written),
            "no_paid_GPU": True,
            "no_oracle_access": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", required=True, type=Path, nargs="+")
    parser.add_argument("--revision", required=True,
                        help="actual pinned full 40-hex Hugging Face dataset snapshot revision")
    parser.add_argument("--output-dir", type=Path,
                        default=Path("dist/datasets/swe_rebench_v2_metadata_only"))
    args = parser.parse_args(argv)
    print(json.dumps(inspect_snapshot(args.parquet, args.revision,
                                      args.output_dir), indent=2))
    print("NOT AN EXECUTABLE TASK BENCHMARK / DO NOT EXPOSE UPSTREAM GOLD PATCHES")


if __name__ == "__main__":
    main()
