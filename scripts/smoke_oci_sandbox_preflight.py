"""Print a non-executable OCI launch profile for a FAKE digest.

Absolutely no image is fetched, container is run, code is loaded or sandbox
security demonstrated. The sha256 digest below is purely a syntactic fixture.
"""
import json

from ucode.oci_sandbox_preflight import (
    propose_first_party_container,validate_dry_run_plan,
)


def main():
    image="docker.io/library/python@sha256:"+"a"*64
    plan=propose_first_party_container(image)
    status=validate_dry_run_plan(plan)
    if not status.startswith("STRUCTURAL_DRY_RUN"):
        raise AssertionError("dry-run plan unexpectedly promoted")
    if plan.executed or plan.permitted_to_execute_untrusted_repositories:
        raise AssertionError("unauthorized real execution")
    print(json.dumps({
        "stage":plan.stage,
        "status":status,
        "image_ref":plan.image_ref,
        "IMAGE_DIGEST_IS_FAKE_SYNTAX_FIXTURE":True,
        "canonical_argv":list(plan.argv),
        "argv_sha256":plan.argv_sha256,
        "docker_invoked":False,
        "real_sandbox_verified":False,
        "network_denial_verified":plan.network_denial_observed,
        "rootless_daemon_verified":plan.runtime_daemon_rootless_verified,
        "all_five_real_meter_caps_enforced":plan.independently_attested_five_resource_limits,
        "third_party_repo_execution_permitted":plan.permitted_to_execute_untrusted_repositories,
        "wall_supervisor_implemented":False,
        "hidden_oracle_isolated":False,
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
