"""Fully SYNTHETIC EHVI wiring example; NOT a performance comparison."""
import json
from dataclasses import asdict

from ucode.acquisition import AcquisitionProposal, ParetoPoint, select_ehvi_action


def main():
    archive = [ParetoPoint(.55, .8), ParetoPoint(.8, .5)]
    proposals = [
        AcquisitionProposal("generate", .72, .08, .65, .1, .8, 3),
        AcquisitionProposal("repair", .82, .1, .55, .07, .75, 2),
    ]
    # Tests/static analysis are *information* actions; model separately via voi.py.
    chosen = select_ehvi_action(archive, proposals, remaining_budget=4,
                                samples=256, seed=7)
    print(json.dumps({
        "warning": "SYNTHETIC prediction inputs; not real results",
        "selected_action": asdict(chosen) if chosen else None,
    }, indent=2))


if __name__ == "__main__":
    main()
