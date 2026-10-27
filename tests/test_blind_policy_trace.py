"""Policy/evaluator separation and budget accounting, all offline mocks."""
import hashlib
import unittest

from ucode.blind_policy_trace import (
    BlindAction, PublicToolReceipt, run_blind_policy,
)
from ucode.task_view_boundary import parse_agent_task_view
from ucode.vector_policy import ResourceVector as RV


class BlindPolicyTraceTests(unittest.TestCase):
    def setUp(self):
        spec = "Pre-fix requirement from an independently approved record."
        self.task = parse_agent_task_view({
            "repository": "owner/repo", "base_sha": "a" * 40,
            "prefixed_spec": spec,
            "spec_sha256": hashlib.sha256(spec.encode()).hexdigest(),
        })
        self.budget = RV(tokens=100, test_calls=2, gpu_seconds=5,
                         cpu_seconds=10, wall_seconds=20)

    def test_held_out_evaluator_not_called_and_no_verdict_visible(self):
        calls, observed = [], []
        plan = ("generate", "test", "release")
        def policy(state):
            observed.append(state)
            return BlindAction(plan[len(state.history)], RV(tokens=10) if not state.history
                               else RV(test_calls=1) if len(state.history) == 1 else RV())
        def tool(action, task, prior, history):
            calls.append(action.kind)
            if action.kind == "generate":
                return PublicToolReceipt("generate", RV(tokens=7), patch="patch A")
            return PublicToolReceipt("test", RV(test_calls=1), feedback="public lint")
        result = run_blind_policy(self.task, self.budget, policy, tool)
        self.assertEqual(result.status, "RELEASED_PENDING_INDEPENDENT_EVALUATION")
        self.assertEqual(calls, ["generate", "test"])
        self.assertEqual(len(observed), 3)
        self.assertEqual([h.kind for h in result.history], ["generate", "test"])
        self.assertEqual(result.remaining.tokens, 93)
        self.assertEqual(result.remaining.test_calls, 1)
        self.assertEqual(result.released_patch_sha256,
                         hashlib.sha256(b"patch A").hexdigest())
        self.assertFalse(any(hasattr(state, "oracle_id") or hasattr(state, "gold_label")
                             for state in observed))

    def test_receipt_cannot_claim_hidden_evaluator_fields(self):
        with self.assertRaises(TypeError):
            PublicToolReceipt("test", RV(test_calls=1),
                              oracle_id="secret-suite")
        with self.assertRaises(TypeError):
            PublicToolReceipt("test", RV(test_calls=1),
                              gold_correct=True)
        with self.assertRaises(ValueError):
            PublicToolReceipt("test", RV(test_calls=1), patch="gold patch")

    def test_five_caps_are_hard_even_when_other_dimensions_available(self):
        for field in ("tokens", "test_calls", "gpu_seconds", "cpu_seconds",
                      "wall_seconds"):
            dispatched = []
            costs = {"tokens": 101, "test_calls": 3, "gpu_seconds": 6,
                     "cpu_seconds": 11, "wall_seconds": 21}
            policy = lambda _: BlindAction("generate", RV(**{field: costs[field]}))
            outcome = run_blind_policy(
                self.task, self.budget, policy,
                lambda *args: dispatched.append(True))
            with self.subTest(field=field):
                self.assertEqual(outcome.status, "BUDGET_BLOCKED")
                self.assertEqual(dispatched, [])

    def test_overreported_tool_cost_halts_and_preserves_conservative_reservation(self):
        result = run_blind_policy(
            self.task, self.budget,
            lambda state: BlindAction("generate", RV(tokens=10)),
            lambda *args: PublicToolReceipt("generate", RV(tokens=11), patch="patch"))
        self.assertEqual(result.status, "TOOL_COST_OVERRUN")
        self.assertFalse(result.accounting_verified)
        self.assertEqual(result.remaining.tokens, 90)
        self.assertEqual(result.history, ())
        self.assertIsNone(result.released_patch)

    def test_failed_tool_never_releases_and_meter_is_unknown(self):
        def fail(*args):
            raise RuntimeError("do not show secret error content to policy")
        result = run_blind_policy(self.task, self.budget,
                                  lambda _: BlindAction("generate", RV(tokens=10)),
                                  fail)
        self.assertEqual(result.status, "TOOL_FAILED_COST_UNVERIFIED")
        self.assertFalse(result.accounting_verified)
        self.assertEqual(result.remaining.tokens, 90)
        self.assertEqual(result.history, ())
        self.assertIsNone(result.released_patch)

    def test_wrong_action_receipt_fails_closed(self):
        result = run_blind_policy(self.task, self.budget,
                                  lambda _: BlindAction("generate", RV(tokens=10)),
                                  lambda *args: PublicToolReceipt(
                                      "test", RV(test_calls=1), feedback="fine"))
        self.assertEqual(result.status, "TOOL_RECEIPT_INVALID")
        self.assertFalse(result.accounting_verified)

    def test_no_candidate_cannot_release_repair_or_test(self):
        for kind in ("release", "repair", "test", "static_analysis"):
            result = run_blind_policy(
                self.task, self.budget,
                lambda _: BlindAction(kind, RV() if kind == "release" else RV(tokens=1)),
                lambda *args: self.fail("tool should not run"))
            with self.subTest(kind=kind):
                self.assertTrue(result.status.startswith("INVALID_"))
                self.assertIsNone(result.released_patch)

    def test_abstention_counts_without_oracle_or_tool_call(self):
        result = run_blind_policy(
            self.task, self.budget,
            lambda _: BlindAction("abstain", RV()),
            lambda *args: self.fail("no dispatch on abstain"))
        self.assertEqual(result.status, "ABSTAINED")
        self.assertEqual(result.remaining, self.budget)
        self.assertIsNone(result.released_patch)

    def test_policy_task_view_and_budget_are_typed(self):
        with self.assertRaises(TypeError):
            run_blind_policy({"gates": []}, self.budget, lambda x: None, lambda *x: None)
        with self.assertRaises(TypeError):
            run_blind_policy(self.task, {"tokens": 5}, lambda x: None, lambda *x: None)
        with self.assertRaises(ValueError):
            BlindAction("test", RV())
        with self.assertRaises(ValueError):
            BlindAction("release", RV(tokens=1))

    def test_repeatable_trace_with_fixed_mock_policy(self):
        def policy(s):
            return BlindAction("generate", RV(tokens=3)) if not s.history else BlindAction("release", RV())
        def tool(*args):
            return PublicToolReceipt("generate", RV(tokens=2), patch="fixed patch")
        x = run_blind_policy(self.task, self.budget, policy, tool)
        y = run_blind_policy(self.task, self.budget, policy, tool)
        self.assertEqual(x, y)
        self.assertTrue(x.accounting_verified)
        self.assertEqual(x.status, "RELEASED_PENDING_INDEPENDENT_EVALUATION")


if __name__ == "__main__":
    unittest.main()
