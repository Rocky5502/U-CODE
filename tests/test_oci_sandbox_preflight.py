"""Adversarial dry-run OCI launch tests; no Docker, network or repo execution."""
from dataclasses import replace
from copy import deepcopy
import json
import unittest

from ucode.oci_sandbox_preflight import (
    DryRunLimits, propose_first_party_container,
    validate_dry_run_plan, check_untrusted_inspect_shape,
)

IMG="docker.io/library/python@sha256:"+"a"*64


def fake_inspect(plan):
    """Caller-supplied, UNTRUSTED JSON that must not be called attestation."""
    limits=plan.limits
    mem=limits.memory_mib*1024*1024
    return {
        "Config":{
            "Image":plan.image_ref,"User":"65534:65534","WorkingDir":"/tmp",
            "Entrypoint":["/usr/local/bin/python3"],
            "Cmd":["-I","-S","-c",
                   "print('U-CODE synthetic OCI preflight fixture')"],
        },
        "HostConfig":{
            "NetworkMode":"none",
            "PidMode":"private","IpcMode":"private",
            "UTSMode":"private","CgroupnsMode":"private",
            "ReadonlyRootfs":True,
            "Privileged":False,"CapAdd":[],"CapDrop":["ALL"],
            "SecurityOpt":["no-new-privileges"],
            "Binds":[],"Mounts":[],"Devices":[],"DeviceRequests":[],
            "PidsLimit":limits.max_pids,
            "Memory":mem,"MemorySwap":mem,
            "NanoCpus":1000000000,
            "Tmpfs":{
                "/tmp":"rw,nosuid,nodev,noexec,size=67108864,uid=65534,gid=65534"
            },
            "Ulimits":[
                {"Name":"cpu","Soft":limits.cpu_seconds_per_process,
                 "Hard":limits.cpu_seconds_per_process},
                {"Name":"nofile","Soft":64,"Hard":64},
            ],
        },
        "Mounts":[],
        "NetworkSettings":{"Networks":{"none":{}}},
    }


class OciDryRunPreflightTests(unittest.TestCase):
    def setUp(self):
        self.plan=propose_first_party_container(IMG)

    def test_canonical_plan_does_not_claim_runtime_security(self):
        self.assertEqual(validate_dry_run_plan(self.plan),
                         "STRUCTURAL_DRY_RUN_ONLY_NOT_HARDENED_CONTAINER")
        self.assertFalse(self.plan.executed)
        self.assertFalse(self.plan.permitted_to_execute_untrusted_repositories)
        self.assertFalse(self.plan.runtime_daemon_rootless_verified)
        self.assertFalse(self.plan.network_denial_observed)
        self.assertFalse(self.plan.filesystem_isolation_observed)
        self.assertFalse(self.plan.runtime_seccomp_verified)
        self.assertFalse(self.plan.independently_attested_five_resource_limits)

    def test_no_shell_network_mount_or_root_in_canonical_command(self):
        args=self.plan.argv
        for required in ("--network=none","--read-only","--cap-drop=ALL",
                         "--security-opt=no-new-privileges",
                         "--pid=private","--ipc=private","--uts=private",
                         "--cgroupns=private","--user=65534:65534","--pull=never",
                         "--tmpfs=/tmp:rw,nosuid,nodev,noexec,size=67108864,uid=65534,gid=65534",
                         "--memory=268435456","--memory-swap=268435456",
                         "--pids-limit=32","--ulimit=cpu=2:2"):
            self.assertIn(required,args)
        self.assertEqual(args[0:2],("docker","run"))
        self.assertNotIn("--privileged",args)
        self.assertNotIn("--network=host",args)
        self.assertNotIn("-v",args)
        self.assertNotIn("--mount",args)
        self.assertNotIn("sh",args)
        self.assertNotIn("bash",args)
        self.assertEqual(args[-4:-1],("-I","-S","-c"))
        self.assertTrue(args[-1].startswith("print("))

    def test_arg_order_and_hash_deterministic(self):
        other=propose_first_party_container(IMG)
        self.assertEqual(other,self.plan)
        self.assertEqual(len(self.plan.argv_sha256),64)
        self.assertEqual(len(json.dumps(other.argv)),len(json.dumps(self.plan.argv)))

    def test_bad_image_identity_fails_closed(self):
        for bad in ("python:3.11","python","python@sha256:abc",
                    "python@sha256:"+"z"*64,
                    "../python@sha256:"+"a"*64,
                    "-e@sha256:"+"a"*64,
                    "docker.io/a@sha256:"+"a"*64+" --network host",
                    "/host/path@sha256:"+"a"*64,
                    "x//y@sha256:"+"a"*64+" extra",
                    "",None,123,True):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                propose_first_party_container(bad)

    def test_hard_bounded_limit_validation(self):
        for field,bads in (
            ("memory_mib",[0,127,4097,-1,True,256.0]),
            ("max_pids",[0,65,True,4.0]),
            ("cpu_seconds_per_process",[0,11,True,2.0]),
            ("max_wall_seconds_for_future_supervisor",[0,21,True,3.0])):
            for bad in bads:
                with self.subTest(field=field,bad=bad),self.assertRaises(ValueError):
                    replace(DryRunLimits(),**{field:bad})

    def test_cannot_tamper_command_arguments(self):
        for evil in ("--privileged","--network=host","--mount=/etc:/host",
                     "--device=/dev/kvm","--cap-add=SYS_ADMIN"):
            changed=replace(self.plan,argv=self.plan.argv+(evil,))
            with self.subTest(evil=evil),self.assertRaises(ValueError):
                validate_dry_run_plan(changed)

    def test_cannot_promote_structure_into_isolation_attestation(self):
        for field in (
            "executed","runtime_daemon_rootless_verified","network_denial_observed",
            "filesystem_isolation_observed","runtime_seccomp_verified",
            "independently_attested_five_resource_limits",
            "permitted_to_execute_untrusted_repositories"):
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,"falsely promoted"):
                validate_dry_run_plan(replace(self.plan,**{field:True}))

    def test_cannot_forge_digest(self):
        with self.assertRaises(ValueError):
            validate_dry_run_plan(replace(self.plan,argv_sha256="f"*64))

    def test_cannot_use_arbitrary_python_code(self):
        argv=list(self.plan.argv)
        argv[-1]="import os; os.system('id')"
        with self.assertRaises(ValueError):
            validate_dry_run_plan(replace(self.plan,argv=tuple(argv)))

    def test_caller_supplied_inspect_is_only_structure(self):
        a=check_untrusted_inspect_shape(self.plan,fake_inspect(self.plan))
        self.assertTrue(a.declared_profile_matches)
        self.assertEqual(a.command_sha256,self.plan.argv_sha256)
        self.assertFalse(a.externally_authenticated)
        self.assertFalse(a.measured_network_isolation)
        self.assertFalse(a.host_daemon_rootless_proven)
        self.assertFalse(a.independent_seccomp_proven)
        self.assertFalse(a.filesystem_containment_proven)
        self.assertFalse(a.approved_external_task_runner)

    def test_inspect_missing_config_rejected(self):
        for field in ("Config","HostConfig","NetworkSettings","Mounts"):
            malformed=fake_inspect(self.plan)
            del malformed[field]
            with self.subTest(field=field),self.assertRaises((ValueError,TypeError)):
                check_untrusted_inspect_shape(self.plan,malformed)

    def test_inspect_privilege_or_no_new_privileges_failure(self):
        for key,evil in (("Privileged",True),("CapAdd",["SYS_ADMIN"]),
                         ("CapDrop",[]),("SecurityOpt",[]),
                         ("ReadonlyRootfs",False),("NetworkMode","host"),
                         ("PidMode","host"),("IpcMode","host"),
                         ("UTSMode","host"),("CgroupnsMode","host")):
            doc=fake_inspect(self.plan)
            doc["HostConfig"][key]=evil
            with self.subTest(key=key),self.assertRaises(ValueError):
                check_untrusted_inspect_shape(self.plan,doc)

    def test_inspect_mount_and_devices_rejected(self):
        for field,evil in (("Binds",["/etc:/host"]),("Mounts",["host"]),
                           ("Devices",["/dev/kvm"]),("DeviceRequests",["gpu"])):
            doc=fake_inspect(self.plan)
            doc["HostConfig"][field]=evil
            with self.subTest(field=field),self.assertRaises(ValueError):
                check_untrusted_inspect_shape(self.plan,doc)
        doc=fake_inspect(self.plan)
        doc["Mounts"]=[{"Source":"/etc"}]
        with self.assertRaises(ValueError):
            check_untrusted_inspect_shape(self.plan,doc)

    def test_inspect_bad_memory_cpu_pid_limits_rejected(self):
        for key,evil in (("Memory",0),("MemorySwap",0),
                         ("NanoCpus",0),("PidsLimit",0)):
            doc=fake_inspect(self.plan)
            doc["HostConfig"][key]=evil
            with self.subTest(key=key),self.assertRaises(ValueError):
                check_untrusted_inspect_shape(self.plan,doc)

    def test_inspect_root_or_image_mutation_rejected(self):
        for key,evil in (("User","0"),("Image","python:latest"),
                         ("WorkingDir","/"),("Entrypoint",["/bin/bash"]),
                         ("Cmd",["-c","import os"])):
            doc=fake_inspect(self.plan)
            doc["Config"][key]=evil
            with self.subTest(key=key),self.assertRaises(ValueError):
                check_untrusted_inspect_shape(self.plan,doc)

    def test_inspect_ulimit_and_tmpfs_tampering_rejected(self):
        for key,evil in (("Ulimits",[]),("Tmpfs",{})):
            doc=fake_inspect(self.plan)
            doc["HostConfig"][key]=evil
            with self.subTest(key=key),self.assertRaises(ValueError):
                check_untrusted_inspect_shape(self.plan,doc)

    def test_inspect_wrong_network_attachment_rejected(self):
        doc=fake_inspect(self.plan)
        doc["NetworkSettings"]["Networks"]={"bridge":{}}
        with self.assertRaisesRegex(ValueError,"network"):
            check_untrusted_inspect_shape(self.plan,doc)

    def test_no_executable_runtime_object_exposed(self):
        import ucode.oci_sandbox_preflight as module
        self.assertFalse(hasattr(module,"run"))
        self.assertFalse(hasattr(module,"execute_untrusted_code"))
        self.assertFalse(hasattr(module,"subprocess"))

    def test_inspect_data_forgery_does_not_set_approval_even_with_perfect_shape(self):
        doc=fake_inspect(self.plan)
        doc["externally_authenticated"]=True
        doc["oracle_passed"]=True
        res=check_untrusted_inspect_shape(self.plan,doc)
        self.assertFalse(res.externally_authenticated)
        self.assertFalse(res.approved_external_task_runner)

    def test_future_supervisor_deadline_is_not_silently_enforced(self):
        self.assertIn("max_wall_seconds_for_future_supervisor",self.plan.limits.__dict__)
        self.assertFalse(self.plan.independently_attested_five_resource_limits)


if __name__=="__main__":
    unittest.main()
