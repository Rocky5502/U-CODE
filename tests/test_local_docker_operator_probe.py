"""OCI operator probe tests: all external Docker calls MOCKED, never run."""
from unittest.mock import patch
import unittest

from scripts.probe_local_oci_first_party import probe_local_first_party_oci

IMG = "docker.io/library/python@sha256:" + "a"*64


def dummy(tokens, timeout=5):
    if tokens[:3] == ("docker", "context", "inspect"):
        return '"unix:///run/user/1000/docker.sock"'
    if tokens[:2] == ("docker", "info"):
        return '["name=seccomp,profile=builtin","name=rootless"]'
    if tokens[:3] == ("docker", "image", "inspect"):
        return '["' + IMG + '"]'
    if tokens[:2] == ("docker", "run"):
        return "U-CODE synthetic OCI preflight fixture"
    raise AssertionError("unrecognized Docker call")


class LocalDockerOperatorProbeTests(unittest.TestCase):
    def test_dry_run_never_uses_docker_or_promotes_research(self):
        with patch("scripts.probe_local_oci_first_party._local_docker_command") as cmd:
            r=probe_local_first_party_oci(IMG)
        cmd.assert_not_called()
        self.assertFalse(r["fixed_fixture_executed"])
        self.assertFalse(r["docker_probed"])
        self.assertFalse(r["permitted_to_execute_third_party_code"])
        self.assertEqual(r["independently_admitted_real_repository_tasks"],0)

    def test_mocked_rootless_local_first_party_only(self):
        seen=[]
        def spy(tokens,timeout=5):
            seen.append(tuple(tokens))
            return dummy(tuple(tokens),timeout)
        with patch.dict("os.environ",{"DOCKER_HOST":"","DOCKER_CONTEXT":""}):
            with patch("scripts.probe_local_oci_first_party._local_docker_command",
                       side_effect=spy):
                r=probe_local_first_party_oci(IMG,execute=True)
        self.assertTrue(r["fixed_fixture_executed"])
        self.assertTrue(r["docker_reported_rootless"])
        self.assertFalse(r["real_trial_approved"])
        self.assertFalse(r["independently_authenticated_isolation"])
        self.assertFalse(r["five_resource_meter_authenticated"])
        self.assertEqual(len(seen),4)
        docker_run=seen[-1]
        self.assertIn("--network=none",docker_run)
        self.assertIn("--pull=never",docker_run)
        self.assertIn("--read-only",docker_run)
        self.assertIn("--cap-drop=ALL",docker_run)
        self.assertNotIn("-v",docker_run)
        self.assertNotIn("--mount",docker_run)
        self.assertEqual(docker_run[-1],
                         "print('U-CODE synthetic OCI preflight fixture')")

    def test_reject_remote_DOCKER_HOST_and_DOCKER_CONTEXT_without_subprocess(self):
        for key,val in (
                ("DOCKER_HOST","tcp://127.0.0.1:2375"),
                ("DOCKER_CONTEXT","remote-host")):
            with patch.dict("os.environ",
                            {"DOCKER_HOST":"","DOCKER_CONTEXT":"",key:val}):
                with patch("scripts.probe_local_oci_first_party._local_docker_command") as cmd:
                    with self.subTest(key=key), self.assertRaisesRegex(
                            ValueError,"environment-selected"):
                        probe_local_first_party_oci(IMG,execute=True)
                    cmd.assert_not_called()

    def test_reject_remote_context_from_docker_output(self):
        def bad(tokens,timeout=5):
            if tokens[:3] == ("docker","context","inspect"):
                return '"tcp://example.org:2376"'
            return dummy(tuple(tokens),timeout)
        with patch.dict("os.environ",{"DOCKER_HOST":"","DOCKER_CONTEXT":""}):
            with patch("scripts.probe_local_oci_first_party._local_docker_command",
                       side_effect=bad):
                with self.assertRaisesRegex(ValueError,"local Unix socket"):
                    probe_local_first_party_oci(IMG,execute=True)

    def test_reject_rootful_daemon(self):
        def bad(tokens,timeout=5):
            if tokens[:2] == ("docker","info"):
                return '["name=seccomp,profile=builtin"]'
            return dummy(tuple(tokens),timeout)
        with patch.dict("os.environ",{"DOCKER_HOST":"","DOCKER_CONTEXT":""}):
            with patch("scripts.probe_local_oci_first_party._local_docker_command",
                       side_effect=bad):
                with self.assertRaisesRegex(ValueError,"rootless"):
                    probe_local_first_party_oci(IMG,execute=True)

    def test_missing_digest_pinned_image_rejects_before_container_run(self):
        calls=[]
        def bad(tokens,timeout=5):
            calls.append(tuple(tokens))
            if tokens[:3] == ("docker","image","inspect"):
                return "[]"
            return dummy(tuple(tokens),timeout)
        with patch.dict("os.environ",{"DOCKER_HOST":"","DOCKER_CONTEXT":""}):
            with patch("scripts.probe_local_oci_first_party._local_docker_command",
                       side_effect=bad):
                with self.assertRaisesRegex(ValueError,"local cache"):
                    probe_local_first_party_oci(IMG,execute=True)
        self.assertFalse(any(args[:2]==("docker","run") for args in calls))

    def test_stdout_injection_or_nonexact_result_rejected(self):
        def bad(tokens,timeout=5):
            if tokens[:2] == ("docker","run"):
                return "SUCCESS\\nESCAPED"
            return dummy(tuple(tokens),timeout)
        with patch.dict("os.environ",{"DOCKER_HOST":"","DOCKER_CONTEXT":""}):
            with patch("scripts.probe_local_oci_first_party._local_docker_command",
                       side_effect=bad):
                with self.assertRaisesRegex(ValueError,"unexpected"):
                    probe_local_first_party_oci(IMG,execute=True)

    def test_invalid_image_and_non_boolean_opt_in_fail_before_probing(self):
        with patch("scripts.probe_local_oci_first_party._local_docker_command") as call:
            with self.assertRaises(ValueError):
                probe_local_first_party_oci("python:latest",execute=False)
            with self.assertRaises(TypeError):
                probe_local_first_party_oci(IMG,execute=1)
            call.assert_not_called()


if __name__=="__main__":
    unittest.main()
