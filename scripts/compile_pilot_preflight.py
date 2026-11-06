"""Print a strict, read-only real-source G5/M4 pilot readiness report.

No GitHub network traffic, model call, third-party code execution, Docker
launch, original source clone, or evaluator oracle access is made.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ucode.pilot_preflight import build_pilot_preflight


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None,
                        help="Write the informational review-only JSON report")
    parser.add_argument("--require-ready", action="store_true",
                        help="Fail with exit 2 until a separately approved pilot exists")
    args = parser.parse_args(argv)
    report = build_pilot_preflight()
    data = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    print(data, end="")
    if args.require_ready and report["qualified_executable_tasks"] == 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
