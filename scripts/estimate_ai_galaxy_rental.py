"""Dry-run rental-day estimator for six fixed U-CODE LLM checkpoints.

Accepts an EXPLICIT user-observed scenario minutes/assignment; never guesses
runtime or claims that source-discovery rows are eligible executable tasks.
No GPU provisioning, payment, dataset execution, remote API or model inference.
"""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from scripts.plan_ai_galaxy_six_models import inspect_plan, load_plan


@dataclass(frozen=True)
class RentalScenario:
    task_count: int
    policy_count: int
    seeds_per_cell: int
    minutes_per_assignment: Decimal
    provider_rmb_per_hour: Decimal
    overhead_fraction: Decimal = Decimal("0.25")
    model_count: int = 6
    gpu_count: int = 1

    def __post_init__(self):
        for field in ("task_count", "policy_count", "seeds_per_cell",
                      "model_count", "gpu_count"):
            value = getattr(self, field)
            if type(value) is not int or value < 1:
                raise ValueError(field + " must be a positive integer")
        if self.model_count != 6 or self.gpu_count != 1:
            raise ValueError("this budget only supports all six models on one A100")
        if self.policy_count > 8:
            raise ValueError("registered study has at most eight prospective policies")
        for field in ("minutes_per_assignment", "provider_rmb_per_hour",
                      "overhead_fraction"):
            value = getattr(self, field)
            if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
                raise ValueError(field + " must be finite and nonnegative")
        if self.minutes_per_assignment <= 0:
            raise ValueError("measured/scenario minutes per assignment must be >0")
        if self.overhead_fraction > 10:
            raise ValueError("overhead assumption above 1000% rejected")

    @property
    def assignments(self):
        return (self.task_count*self.policy_count*self.seeds_per_cell
                *self.model_count)

    @property
    def gpu_hours(self):
        return (Decimal(self.assignments)*self.minutes_per_assignment
                * (1+self.overhead_fraction)/60)

    @property
    def gpu_days(self):
        return self.gpu_hours/24

    @property
    def nominal_rmb(self):
        return self.gpu_hours*self.provider_rmb_per_hour

    def to_dict(self):
        return {
            "model_count": 6, "gpu_type": "NVIDIA A100 80GB", "gpu_count": 1,
            "approved_executable_task_count": "NOT_VERIFIED_BY_THIS_TOOL",
            "task_count_hypothetical": self.task_count,
            "policy_count_hypothetical": self.policy_count,
            "seeds_hypothetical": self.seeds_per_cell,
            "assignments_hypothetical": self.assignments,
            "minutes_per_assignment_assumed_not_measured_by_tool": str(self.minutes_per_assignment),
            "extra_overhead_fraction_assumed": str(self.overhead_fraction),
            "gpu_hours_scenario": str(self.gpu_hours),
            "gpu_days_scenario": str(self.gpu_days),
            "provider_rate_promotional_not_checkout_verified_RMB_per_hour": str(self.provider_rmb_per_hour),
            "estimated_rental_RMB_excluding_storage_RAM_network": str(self.nominal_rmb),
            "runnable_now": False,
            "experiment_results_generated": False,
        }


def scenario_from_cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=int, default=40,
                        help="HYPOTHETICAL qualified tasks; default 40")
    parser.add_argument("--policies", type=int, default=2,
                        help="HYPOTHETICAL compared policies; default 2")
    parser.add_argument("--seeds", type=int, default=1,
                        help="HYPOTHETICAL seeds; default 1")
    parser.add_argument("--minutes-per-assignment", required=True,
                        help="REQUIRED measured/scenario duration, never auto-estimated")
    parser.add_argument("--rmb-per-hour", default="8",
                        help="Provider promotional assumption, not checkout quote")
    parser.add_argument("--overhead-fraction", default="0.25",
                        help="Explicit extra time fraction; default 0.25")
    args = parser.parse_args(argv)
    selected, deployment = load_plan()
    if len(inspect_plan(selected, deployment)) != 6:
        raise ValueError("invalid six-model GPU deployment identity")
    try:
        return RentalScenario(
            args.tasks, args.policies, args.seeds,
            Decimal(args.minutes_per_assignment),
            Decimal(args.rmb_per_hour),
            Decimal(args.overhead_fraction),
        )
    except InvalidOperation as exc:
        raise ValueError("invalid numeric scenario assumption") from exc


def main():
    estimate = scenario_from_cli()
    print(json.dumps(estimate.to_dict(), indent=2))
    print("NOT A PURCHASE ORDER; NOT MEASURED THROUGHPUT OR VERIFIED DATASET.")
    print("Hold real experiments until independent evaluator/runner/tasks pass.")


if __name__ == "__main__":
    main()
