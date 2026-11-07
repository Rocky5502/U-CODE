"""Export deterministic PUBLIC ONLY U-CODE critical-path JSON/Markdown.

Source-only metadata, not inferred task approval or model execution. This
script never reads reviewer-completed private forms, downloads weights,
executes upstream PHP/Go, accesses oracle gold, or starts GPU work.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from ucode.critical_path import build_critical_path, critical_path_markdown

_REPORT_FILES=("CRITICAL_PATH_STATUS.json", "REMAINING_WORK.md")


def export_critical_path(directory: Path) -> dict:
    report=build_critical_path()
    dest=Path(directory)
    if dest.is_symlink():
        raise ValueError("will not export readiness to symlink directory")
    dest.mkdir(parents=True,exist_ok=True)
    files={
        _REPORT_FILES[0]:json.dumps(report,sort_keys=True,indent=2)+"\n",
        _REPORT_FILES[1]:critical_path_markdown(report),
    }
    for name,body in files.items():
        path=dest/name
        if path.is_symlink():
            raise ValueError("will not overwrite symlinked readiness file")
        path.write_text(body,encoding="utf-8")
    integrity={
        "status":"PUBLIC_SOURCE_ONLY_NOT_REAL_STUDY",
        "verified_report_schema":"1.0",
        "hash_algorithm":"sha256",
        "files_sha256":{
            name:sha256(files[name].encode("utf-8")).hexdigest()
            for name in sorted(files)
        },
        "unqualified_experiment":True,
        "no_hidden_oracle_or_reviewer_private_inputs":True,
        "real_task_admissions":0,
    }
    path=dest/"CRITICAL_PATH_INTEGRITY.json"
    if path.is_symlink():
        raise ValueError("will not overwrite symlinked receipt")
    path.write_text(json.dumps(integrity,sort_keys=True,indent=2)+"\n",
                    encoding="utf-8")
    return {
        "status":report["stage"],
        "files":list(_REPORT_FILES)+["CRITICAL_PATH_INTEGRITY.json"],
        "major_milestone_exit_criteria_unverified":
            report["milestone_accounting"]["still_without_full_exit_evidence"],
        "pilot_admission_checks_pending":
            report["independent_pilot_admission"]["open_checks"],
        "qualified_executable_tasks":0,
        "real_model_runs":0,
        "primary_effect":None,
        "overall_percent_complete":None,
    }


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,
                        default=Path("dist/ucode-critical-path"))
    parser.add_argument("--require-empirical-ready",action="store_true",
                        help="Exit 2 while external experiment gates remain blocked")
    args=parser.parse_args(argv)
    out=export_critical_path(args.output_dir)
    print(json.dumps(out,sort_keys=True,indent=2))
    if args.require_empirical_ready and out["qualified_executable_tasks"]==0:
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
