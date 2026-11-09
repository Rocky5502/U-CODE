"""Review-only cross-ledger S05–S10 sprint checkpoint; never a runner permit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ucode.remaining_stage_evidence import build_remaining_stage_evidence


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None,
                        help="optional PUBLIC report path, no private evidence")
    parser.add_argument("--require-real-ready", action="store_true",
                        help="strict gate: expect exit code 2 while real trial blocked")
    args = parser.parse_args(argv)
    report = build_remaining_stage_evidence()
    payload = json.dumps(
        report, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        if args.output.is_symlink():
            raise ValueError("cannot write source-only checkpoint through symlink")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    # A successful internal data crosscheck can NEVER grant execution rights.
    if args.require_real_ready:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
