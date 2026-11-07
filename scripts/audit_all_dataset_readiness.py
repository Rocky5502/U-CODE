"""Export public-only all-source readiness and first-party code inventory.

These files describe catalog metadata and missing independent approvals,
NOT an executable dataset, benchmark pass rate or permitted external run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from hashlib import sha256

from ucode.dataset_code_readiness import audit_dataset_code_readiness,readiness_markdown


def export_all_dataset_readiness(directory:Path)->dict:
    report=audit_dataset_code_readiness()
    dest=Path(directory)
    if dest.is_symlink():
        raise ValueError("output directory cannot be symlinked")
    dest.mkdir(parents=True,exist_ok=True)
    files={
        "ALL_DATASET_READINESS.json":json.dumps(report,sort_keys=True,indent=2)+"\n",
        "ALL_DATASET_CODE_STATUS.md":readiness_markdown(report),
    }
    for name,body in files.items():
        path=dest/name
        if path.is_symlink():
            raise ValueError("status output cannot overwrite symlink")
        path.write_text(body,encoding="utf-8")
    receipt={
        "schema_version":"1.0",
        "status":"PUBLIC_ONLY_NO_EXECUTABLE_DATASETS",
        "sha256":{
            name:sha256(content.encode("utf-8")).hexdigest()
            for name,content in sorted(files.items())
        },
        "independently_qualified_task_count":0,
        "hidden_gold_or_reviewer_evidence_included":False,
    }
    path=dest/"ALL_DATASET_STATUS_SHA256.json"
    if path.is_symlink():
        raise ValueError("receipt output cannot overwrite symlink")
    path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return {
        "status":report["stage"],
        "external_sources":report["dataset_catalog_count"],
        "discovery_prs":report["public_discovery_metadata"]["pr_links"],
        "pilot_checks_pending":report["pilot"]["admission_gates_pending"],
        "model_checkpoints_qualified":report["models"]["qualified_checkpoint_revisions"],
        "real_policy_arms_verified":report["confirmatory_design"]["real_end_to_end_faithful_policy_arms"],
        "qualified_executable_tasks":0,
        "legacy_experiment_config_incompatible":True,
        "outputs":sorted((*files,"ALL_DATASET_STATUS_SHA256.json")),
    }


def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",type=Path,
                   default=Path("dist/ucode-all-datasets-readiness"))
    p.add_argument("--require-runnable",action="store_true",
                   help="Exit 2 if datasets remain unapproved for real execution")
    args=p.parse_args(argv)
    state=export_all_dataset_readiness(args.output_dir)
    print(json.dumps(state,indent=2,sort_keys=True))
    return 2 if args.require_runnable else 0


if __name__=="__main__":
    raise SystemExit(main())
