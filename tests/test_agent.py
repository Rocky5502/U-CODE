import unittest

from ucode.agent import AgentRunner, Verification
from ucode.ollama import generate_local
from ucode.search import ActionEstimate, SearchState


class AgentTests(unittest.TestCase):
    def test_generate_then_verify_is_only_oracle_success(self):
        def gen(task, prior, feedback):
            return "patch: " + task

        def verify(patch):
            return Verification(patch == "patch: fix bug", "sandbox test passed",
                                "pinned-independent-suite")

        def options(state, verification):
            if not state.has_candidate:
                return [ActionEstimate("generate", 1, 0, 0, 2)]
            return [ActionEstimate("test", 0, 1, 0, 1)]

        runner = AgentRunner(gen, verify, lambda patch, feedback: .5, options)
        outcome = runner.run("fix bug", budget=5, policy="fixed_test")
        self.assertEqual(outcome.status, "verified_by_provided_oracle")
        self.assertEqual([a.action for a in outcome.trace], ["generate", "test"])
        self.assertEqual(outcome.total_spent, 3)
        self.assertTrue(outcome.trace[-1].verifier_passed)

    def test_static_analysis_alone_never_counts_as_functional_success(self):
        def proposals(state, evidence):
            if not state.has_candidate:
                return [ActionEstimate("generate", 1, 0, 0, 1)]
            return [ActionEstimate("static_analysis", 0, 1, 1, 1)]
        runner = AgentRunner(
            lambda task, previous, feedback: "patch",
            lambda patch: Verification(True, "hidden tests passed", "hidden-oracle"),
            lambda patch, evidence: .3,
            proposals,
            static_analyzer=lambda patch: Verification(True, "lint passed", "static-linter"),
        )
        result = runner.run("task", budget=2, policy="cost_first")
        self.assertEqual(result.status, "abstained_or_budget_exhausted")
        self.assertEqual([step.action for step in result.trace],
                         ["generate", "static_analysis"])
        self.assertIsNone(result.trace[-1].verifier_passed)

    def test_budget_limits_agent(self):
        runner = AgentRunner(lambda task, prior, feedback: "patch",
                             lambda patch: Verification(True, "pass", "oracle"),
                             lambda patch, evidence: .5,
                             lambda state, out: [ActionEstimate("generate", 1, 0, 0, 5)])
        outcome = runner.run("task", budget=2)
        self.assertEqual(outcome.status, "abstained_or_budget_exhausted")
        self.assertEqual(outcome.total_spent, 0)

    def test_no_remote_ollama(self):
        with self.assertRaises(ValueError):
            generate_local("secret", base_url="https://example.org")

    def test_state_constraints(self):
        with self.assertRaises(ValueError):
            SearchState(-1, .5)
        with self.assertRaises(ValueError):
            SearchState(10, 1.2)


if __name__ == "__main__":
    unittest.main()
