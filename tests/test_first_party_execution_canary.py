"""Actually executes fixed first-party Python repair fixtures only.

All expected outputs are PUBLIC source-controlled canary vectors. This is
not a sealed independent repair oracle and not an admitted benchmark.
"""
from dataclasses import replace
from hashlib import sha256
import json
import subprocess
import unittest
from unittest.mock import patch

from ucode.first_party_execution_canary import (
    ALLOWED_FIRST_PARTY_CANDIDATES, FirstPartyExecutionReceipt,
    _WORKER_SHA256, STAGE, check_first_party_repair_canary,
    run_first_party_execution_canary,
)


class FirstPartyExecutionCanaryTests(unittest.TestCase):
    def test_executes_both_trusted_candidates_and_labels_public_results(self):
        bad, good = (
            run_first_party_execution_canary(candidate)
            for candidate in ALLOWED_FIRST_PARTY_CANDIDATES
        )
        self.assertEqual((bad.attempted_public_cases,bad.passed_public_cases,
                          bad.failed_public_cases),(7,4,3))
        self.assertEqual((good.attempted_public_cases,good.passed_public_cases,
                          good.failed_public_cases),(7,7,0))
        self.assertEqual((bad.worker_source_sha256,good.worker_source_sha256),
                         (_WORKER_SHA256,_WORKER_SHA256))
        self.assertEqual(bad.stage,STAGE)
        self.assertTrue(bad.fixed_first_party_source_executed)

    def test_canary_never_asserts_independent_oracle_or_real_repository(self):
        report=check_first_party_repair_canary()
        self.assertEqual(report["real_repository_tasks_admitted"],0)
        self.assertEqual(report["authenticated_hidden_oracles"],0)
        self.assertEqual(report["real_policy_comparison_results"],0)
        self.assertIsNone(report["qualified_experimental_effect"])
        self.assertFalse(report["untrusted_source_executed"])
        for receipt in report["candidate_receipts"]:
            self.assertFalse(receipt["third_party_source_executed"])
            self.assertFalse(receipt["eligible_as_confirmatory_evidence"])
            self.assertFalse(receipt["sandbox_isolation_verified"])
            self.assertFalse(receipt["held_out_independent_oracle_verified"])
            self.assertFalse(receipt["five_resource_physical_meter_authenticated"])
            self.assertFalse(receipt["llm_inference_executed"])

    def test_arbitrary_code_path_and_string_rejected_before_process_launch(self):
        for bad in ('', '/tmp/evil.py', 'python -c "print(1)"',
                    'stable_unique_repair\nimport os', None, True, 3):
            with self.subTest(value=bad),patch(
                    "ucode.first_party_execution_canary.subprocess.run") as run:
                with self.assertRaisesRegex(ValueError,"two frozen"):
                    run_first_party_execution_canary(bad)
                run.assert_not_called()

    def test_child_process_receives_exact_fixed_source_without_shell(self):
        actual=subprocess.run
        captures=[]
        def spy(cmd,*args,**kwargs):
            captures.append((cmd,kwargs))
            return actual(cmd,*args,**kwargs)
        with patch("ucode.first_party_execution_canary.subprocess.run",side_effect=spy):
            receipt=run_first_party_execution_canary(
                ALLOWED_FIRST_PARTY_CANDIDATES[1])
        self.assertEqual(receipt.passed_public_cases,7)
        self.assertEqual(len(captures),1)
        command,kw=captures[0]
        self.assertEqual(command[1:4],["-I","-S","-c"])
        self.assertNotIn("shell",kw)
        self.assertTrue(kw["cwd"].is_absolute())
        req=json.loads(kw["input"])
        self.assertEqual(set(req),{"candidate","cases"})
        self.assertNotIn("oracle",json.dumps(req).lower())
        self.assertNotIn("expected",json.dumps(req).lower())

    def test_tampered_worker_identity_fails(self):
        result={"candidate":"another", "outputs":[[]]*7}
        process=subprocess.CompletedProcess([],0,json.dumps(result),"")
        with patch("ucode.first_party_execution_canary.subprocess.run",
                   return_value=process):
            with self.assertRaisesRegex(ValueError,"schema or candidate"):
                run_first_party_execution_canary(
                    ALLOWED_FIRST_PARTY_CANDIDATES[0])

    def test_worker_nonzero_and_timeout_fail_closed(self):
        process=subprocess.CompletedProcess([],1,"","failure")
        with patch("ucode.first_party_execution_canary.subprocess.run",
                   return_value=process):
            with self.assertRaisesRegex(RuntimeError,"exited nonzero"):
                run_first_party_execution_canary(
                    ALLOWED_FIRST_PARTY_CANDIDATES[0])
        with patch("ucode.first_party_execution_canary.subprocess.run",
                   side_effect=subprocess.TimeoutExpired([],3)):
            with self.assertRaisesRegex(RuntimeError,"timed out"):
                run_first_party_execution_canary(
                    ALLOWED_FIRST_PARTY_CANDIDATES[0])

    def test_worker_wrong_schema_or_non_integer_fails(self):
        for result in (
            {"candidate":ALLOWED_FIRST_PARTY_CANDIDATES[0],"outputs":[]},
            {"candidate":ALLOWED_FIRST_PARTY_CANDIDATES[0],
             "outputs":[["fake"]]*7},
            {"candidate":ALLOWED_FIRST_PARTY_CANDIDATES[0],
             "outputs":[[True]]*7},
            {"candidate":ALLOWED_FIRST_PARTY_CANDIDATES[0],
             "outputs":[[]]*7,"oracle_passed":True},
        ):
            with self.subTest(result=result):
                process=subprocess.CompletedProcess([],0,json.dumps(result),"")
                with patch("ucode.first_party_execution_canary.subprocess.run",
                           return_value=process):
                    with self.assertRaises(ValueError):
                        run_first_party_execution_canary(
                            ALLOWED_FIRST_PARTY_CANDIDATES[0])

    def test_worker_printing_stderr_fails(self):
        result={"candidate":ALLOWED_FIRST_PARTY_CANDIDATES[0],"outputs":[[]]*7}
        process=subprocess.CompletedProcess([],0,json.dumps(result),"LEAK")
        with patch("ucode.first_party_execution_canary.subprocess.run",
                   return_value=process):
            with self.assertRaisesRegex(ValueError,"unexpected"):
                run_first_party_execution_canary(
                    ALLOWED_FIRST_PARTY_CANDIDATES[0])


if __name__=="__main__":
    unittest.main()
