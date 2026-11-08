"""Operator-facing *nonexecuting* U-CODE experimental phase-0 preparation.

No task checkout, model download, network call, trial, oracle, Docker start
or GPU job; only --probe-gpu triggers a read-only native nvidia-smi query
against the operator's own host. No flag can make an experiment authorized.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from ucode.real_trial_phase0 import (
    build_real_trial_phase0, read_only_nvidia_gpu_survey,
)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hypothetical-tasks", type=int, default=1,
                   help="bounded planning what-if, NOT admitted task IDs")
    p.add_argument("--hypothetical-seeds", type=int, default=1,
                   help="1..3 illustrative, NOT final registered seeds")
    p.add_argument("--probe-gpu", action="store_true",
                   help="Opt-in ONLY to local read-only nvidia-smi GPU inventory")
    p.add_argument("--output", type=Path, default=None,
                   help="Optional write-once status JSON; no private reviewer content")
    p.add_argument("--require-real-ready", action="store_true",
                   help="Always exit 2; no independent trial authorization possible here")
    args = p.parse_args(argv)
    state = build_real_trial_phase0(
        hypothetical_task_slots=args.hypothetical_tasks,
        hypothetical_seed_count=args.hypothetical_seeds,
        gpu_survey=read_only_nvidia_gpu_survey() if args.probe_gpu else None,
    )
    serialized = json.dumps(state, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        if args.output.is_symlink():
            raise ValueError("will not write phase-0 status through symlink")
        if args.output.exists():
            raise FileExistsError("do not overwrite a prior preparation report")
        if not args.output.parent.is_dir():
            raise ValueError("choose an existing output directory")
        # Exclusive-create avoids writing over original frozen manifests.
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(serialized)
    print(serialized, end="")
    return 2 if args.require_real_ready else 0


if __name__ == "__main__":
    raise SystemExit(main())
