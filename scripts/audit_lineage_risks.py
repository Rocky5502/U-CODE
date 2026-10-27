"""Produce standalone, reproducible 120-PR potential-lineage review graph.

No split, duplicate assertion, issue label, reviewer signature, model run or
external source download. Keeps eight-file QC release unchanged.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from scripts.build_clean_pr_dataset import SOURCE, AUDIT_DIR
from scripts.summarize_audit import load_manifest, load_records
from ucode.dataset_curation import build_dataset
from ucode.dataset_quality import validate_release
from ucode.lineage_risk_graph import build_lineage_risk_graph, export_graph_csv


def run(output_dir: Path, *, manifest=SOURCE, audit_dir=AUDIT_DIR):
    mpath = Path(manifest)
    raw = mpath.read_bytes()
    discovery = load_manifest(mpath)
    audits = load_records(audit_dir, discovery)
    clean = build_dataset(discovery, audits, sha256(raw).hexdigest())
    validate_release(clean, audits)
    graph = build_lineage_risk_graph(clean, audits)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    sources = export_graph_csv(graph)
    sources["lineage_graph_report.json"] = (
        json.dumps(graph.summary, sort_keys=True, indent=2) + "\n")
    for name, body in sources.items():
        (out/name).write_text(body, encoding="utf-8")
    digest_report = {
        "stage": "REVIEW_ONLY_NO_CONFIRMED_DUPLICATES_OR_SPLIT",
        "input_manifest_sha256": sha256(raw).hexdigest(),
        "output_sha256": {
            name: sha256(body.encode("utf-8")).hexdigest()
            for name, body in sorted(sources.items())
        },
        "records": len(clean.rows),
        "experiment_eligible": 0,
    }
    (out/"lineage_graph_integrity.json").write_text(
        json.dumps(digest_report, sort_keys=True, indent=2)+"\n",
        encoding="utf-8")
    return graph.summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path,
                   default=Path("dist/ucode-lineage-review"))
    args = p.parse_args(argv)
    print(json.dumps(run(args.output_dir), indent=2, sort_keys=True))
    print("POTENTIAL OVERLAP ONLY; NO ADJUDICATED SPLIT, NO REAL TASKS.")


if __name__ == "__main__":
    main()
