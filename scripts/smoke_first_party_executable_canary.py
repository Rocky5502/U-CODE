"""Run an actual trusted-source public repair canary, NOT a real task study.

No third-party source, hidden test, model inference, Docker or arbitrary
subprocess command is accepted. Outputs are explicit quarantined fixtures.
"""
import json

from ucode.first_party_execution_canary import check_first_party_repair_canary


def main():
    report=check_first_party_repair_canary()
    print(json.dumps(report,sort_keys=True,indent=2))
    if (report["real_repository_tasks_admitted"]!=0 or
            report["real_policy_comparison_results"]!=0):
        raise AssertionError("first-party canary may not be promoted to research results")


if __name__=="__main__":
    main()
