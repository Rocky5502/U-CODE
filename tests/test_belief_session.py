"""Closed-loop BES logic; no external repository execution or oracle labels."""
import unittest

from ucode.belief_session import (
    BeliefSession, finalize_session, plan_session,
    record_candidate, record_evidence,
)
from ucode.budgeted_belief_search import (
    CandidateAction, CandidateScenario, EvidenceAction,
)
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


class VisibleBeliefSessionTests(unittest.TestCase):
    def setUp(self):
        self.rule = ReleaseRule(.1)
        self.prices = ResourcePrices(tokens=.001, test_calls=.01)
        self.budget = ResourceVector(tokens=50, test_calls=2)
        self.a = EvidenceAction("test-one", "test", .8, .8,
                                ResourceVector(test_calls=1))
        self.b = EvidenceAction("test-two", "test", .8, .8,
                                ResourceVector(test_calls=1))

    def test_replan_after_first_positive_evidence(self):
        state = BeliefSession(.5, self.budget)
        proposed = plan_session(state, [self.a, self.b], self.prices,
                                self.rule, horizon=2,
                                assume_independent_diagnostics=True)
        self.assertEqual(proposed.first_action, "test-one")
        updated = record_evidence(state, self.a, True)
        self.assertAlmostEqual(updated.prior, .8)
        self.assertEqual(updated.remaining.test_calls, 1)
        follow_up = plan_session(updated, [self.a, self.b], self.prices,
                                 self.rule, horizon=1)
        self.assertEqual(follow_up.first_action, "test-two")
        final = record_evidence(updated, self.b, True)
        self.assertAlmostEqual(final.prior, 16 / 17)
        self.assertEqual(final.remaining.test_calls, 0)
        self.assertEqual(plan_session(final, [self.a, self.b],
                                      self.prices, self.rule).first_action, "release")
        locked = finalize_session(final, "release", self.rule)
        self.assertEqual(locked.terminal, "release")

    def test_negative_observation_changes_future_decision(self):
        state = record_evidence(BeliefSession(.5, self.budget), self.a, False)
        self.assertAlmostEqual(state.prior, .2)
        decision = plan_session(state, [self.a, self.b],
                                self.prices, self.rule, horizon=1)
        self.assertEqual(decision.first_action, "abstain")

    def test_cannot_purchase_same_action_twice(self):
        used = record_evidence(BeliefSession(.5, self.budget), self.a, True)
        with self.assertRaisesRegex(ValueError, "already consumed"):
            record_evidence(used, self.a, True)

    def test_reject_impossible_visible_diagnostic(self):
        certain = EvidenceAction("certain-negative", "test", 0, 1,
                                 ResourceVector(test_calls=1))
        with self.assertRaisesRegex(ValueError, "impossible positive"):
            record_evidence(BeliefSession(.5, self.budget),
                            certain, True)

    def test_prohibited_label_type_bool_not_integer(self):
        with self.assertRaises(ValueError):
            record_evidence(BeliefSession(.5, self.budget), self.a, 1)

    def test_generate_then_test_without_an_existing_patch(self):
        gen = CandidateAction("gen", "generate",
                              (CandidateScenario(1, .5),),
                              ResourceVector(tokens=40))
        perfect = EvidenceAction("strong-test", "test", 1, 1,
                                 ResourceVector(test_calls=1))
        visible = BeliefSession(None, self.budget)
        plan = plan_session(visible, [gen, perfect], self.prices,
                            self.rule, horizon=2)
        self.assertEqual(plan.first_action, "gen")
        next_state = record_candidate(visible, gen, .5)
        self.assertEqual(next_state.remaining.tokens, 10)
        self.assertEqual(
            plan_session(next_state, [gen, perfect], self.prices,
                         self.rule, horizon=1).first_action, "strong-test")

    def test_failed_repair_preserves_prior_candidate(self):
        repair = CandidateAction("repair", "repair",
                                 (CandidateScenario(1, None),),
                                 ResourceVector(tokens=1))
        state = record_candidate(BeliefSession(.95, self.budget),
                                 repair, None)
        self.assertAlmostEqual(state.prior, .95)
        self.assertEqual(state.events[-1].outcome, "no_usable_candidate")

    def test_reject_forecast_outside_frozen_support(self):
        gen = CandidateAction("gen", "generate",
                              (CandidateScenario(1, .5),),
                              ResourceVector(tokens=1))
        with self.assertRaisesRegex(ValueError, "support"):
            record_candidate(BeliefSession(None, self.budget), gen, .99)

    def test_reject_inspection_without_candidate(self):
        with self.assertRaisesRegex(ValueError, "absent candidate"):
            record_evidence(BeliefSession(None, self.budget), self.a, True)

    def test_reject_insufficient_budget(self):
        state = BeliefSession(.5, ResourceVector(test_calls=0))
        with self.assertRaisesRegex(ValueError, "not feasible"):
            record_evidence(state, self.a, True)

    def test_stop_abstention_and_release_gate(self):
        blocked = BeliefSession(.5, self.budget)
        with self.assertRaisesRegex(ValueError, "fails frozen"):
            finalize_session(blocked, "release", self.rule)
        out = finalize_session(blocked, "abstain", self.rule)
        self.assertEqual(out.terminal, "abstain")
        with self.assertRaisesRegex(ValueError, "already finalized"):
            plan_session(out, [self.a], self.prices, self.rule)
        with self.assertRaisesRegex(ValueError, "already finalized"):
            record_evidence(out, self.a, True)

    def test_known_perfect_positive_maintains_one(self):
        diag = EvidenceAction("perfect", "test", 1, 1,
                              ResourceVector(test_calls=1))
        state = record_evidence(BeliefSession(1.0, self.budget), diag, True)
        self.assertEqual(state.prior, 1)

    def test_session_rejects_invalid_prior(self):
        with self.assertRaises(ValueError):
            BeliefSession(1.2, self.budget)
        with self.assertRaises(ValueError):
            BeliefSession(True, self.budget)

    def test_terminal_release_is_not_evaluator_label(self):
        state = finalize_session(BeliefSession(.95, self.budget),
                                 "release", self.rule)
        self.assertEqual(state.terminal, "release")
        self.assertEqual(state.prior, .95)
        self.assertEqual(len(state.events), 0)


if __name__ == "__main__":
    unittest.main()
