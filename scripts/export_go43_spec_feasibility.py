"""Export source-pinned Go #43 mathematical *review questions*, never test golds.

No network, original external document copies, Go code, test outcomes,
reviewer identities or admission controls. The requested strict mode exits 2
because a public research program cannot authorize a real benchmark task.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from scripts.compile_go43_review_handoff import compile_go43_public_handoff
from ucode.go43_spec_feasibility import build_go43_spec_feasibility_packet
from ucode.pilot_preflight import ROOT

_PLAN = "data/admission/2026-11-07/go43_pre_fix_oracle_review_blueprint_PUBLIC_NO_GOLD.json"

def compile_go43_spec_feasibility(root: Path = ROOT) -> dict:
    base = Path(root)
    plan = json.loads((base / _PLAN).read_text("utf-8"))
    verified = compile_go43_public_handoff(root=base)
    return build_go43_spec_feasibility_packet(plan, verified)

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional public-only JSON report, without golds")
    parser.add_argument("--require-spec-resolved", action="store_true",
                        help="Strict blocked mode: independent spec review remains open (exit 2)")
    args = parser.parse_args(argv)
    report = compile_go43_spec_feasibility()
    text = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        destination = args.output
        if destination.is_symlink():
            raise ValueError("cannot write public review packet via symlink")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
    print(text, end="")
    return 2 if args.require_spec_resolved else 0

if __name__ == "__main__":
    raise SystemExit(main())
