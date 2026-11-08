"""Public-only six-model Hugging Face card observation report for P0-3.

This is not a model download, an independently archived Hub revision, a
license approval, a VRAM benchmark, or permission to run the study.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ucode.public_model_card_audit import build_public_card_audit


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hypothetical-gpu-gib", type=int, default=16,
                        help="what-if capacity, not a probed GPU (default 16 GiB)")
    parser.add_argument("--output", type=Path, default=None,
                        help="write PUBLIC data only, never keys or actual weights")
    parser.add_argument("--require-six-ready", action="store_true",
                        help="strict gate: never treat unsigned Hub tags as approval; exit 2")
    args = parser.parse_args(argv)
    report = build_public_card_audit(
        comparison_capacity_gib=args.hypothetical_gpu_gib)
    encoded = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        if args.output.is_symlink():
            raise ValueError("cannot write public metadata via symlink")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 2 if args.require_six_ready else 0


if __name__ == "__main__":
    raise SystemExit(main())
