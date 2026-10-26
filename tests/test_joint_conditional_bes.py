"""SYNTHETIC adversarial joint-archive conditional BES regression suite."""
from dataclasses import replace
import unittest

from ucode.conditional_bes import ConditionalKernel, ConditionalRow, Observation
from ucode.joint_conditional_bes import (
    CandidateBelief, FrozenJointInputs, ProducerForecast, ProducerOutcome,
    SymbolicCandidateKey, plan_joint_archive, record_joint_archive,
)
from ucode.matched_session import SharedDecision, SharedSession, commit_shared
from ucode.optimized_search import SearchAction, SearchCandidate, SearchState
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule

A, B, C = "a"*64, "b"*64, "c"*64
BUDGET = ResourceVector(tokens=5, test_calls=2, cpu_seconds=2)
GEN = SearchAction("gen", "generate", ResourceVector(tokens=1))
REP = SearchAction("rep", "repair", ResourceVector(tokens=1))
TEST = SearchAction("test", "test", ResourceVector(test_calls=1))
TEST2 = SearchAction("test2", "test", ResourceVector(test_calls=1))
PERFECT = ConditionalKernel((
    ConditionalRow("test", (), 1, 0),
    ConditionalRow("test2", (), 1, 0),
))


def seeded(keys=(A,), cap=8):
    archive = tuple(SearchCandidate(sha, "initial") for sha in keys)
    return SharedSession(
        BUDGET, SearchState(BUDGET, archive, keys[0] if keys else None),
        max_candidates=cap)


def model(priors=((A, .5, "base"),), kernels=(("base", PERFECT),),
          producers=(), horizon=2, max_states=30000,
          prices=ResourcePrices()):
    return FrozenJointInputs(
        tuple(CandidateBelief(*x) for x in priors), kernels, producers,
        prices, ReleaseRule(max_predicted_failure=.1),
        horizon, max_states)


def producer(aid="gen", kind="generate", profile=None, history=(),
             outcomes=(ProducerOutcome(1.0, .5, "fresh"),)):
    return ProducerForecast(aid, kind, profile, history, outcomes)


class JointArchiveTests(unittest.TestCase):
    def test_joint_evidence_value_on_existing_candidate(self):
        p = plan_joint_archive(seeded(), (TEST,), model(horizon=1))
        self.assertEqual((p.decision.action_id, p.decision.target_sha256),
                         ("test", A))
        self.assertGreater(p.expected_proxy_utility, p.stop_utility)

    def test_can_test_non_active_candidate(self):
        p = plan_joint_archive(
            seeded((A, B)), (TEST,),
            model(priors=((A, 0, "base"), (B, .5, "base")), horizon=1))
        self.assertEqual((p.decision.action_id, p.decision.target_sha256),
                         ("test", B))

    def test_deterministic_release_tie_uses_sha(self):
        p = plan_joint_archive(
            seeded((B, A)), (),
            model(priors=((A, .99, "base"), (B, .99, "base"))))
        self.assertEqual((p.decision.kind, p.decision.target_sha256),
                         ("release", A))

    def test_deterministic_action_tie_uses_id(self):
        p = plan_joint_archive(
            seeded(), (TEST2, TEST), model(horizon=1))
        self.assertEqual(p.decision.action_id, "test")

    def test_joint_generate_then_test_symbolic_candidate(self):
        # A one-step generator has zero terminal value (.5 is below the
        # release gate); a second-stage test on its symbolic child has value.
        p = plan_joint_archive(
            seeded(()), (GEN, TEST),
            model(priors=(), kernels=(("fresh", PERFECT),),
                  producers=(producer(),), horizon=2))
        self.assertEqual((p.decision.action_id, p.decision.target_sha256),
                         ("gen", None))
        self.assertGreater(p.expected_proxy_utility, 0)

    def test_one_step_generation_without_future_evidence_abstains(self):
        p = plan_joint_archive(
            seeded(()), (GEN,),
            model(priors=(), kernels=(), producers=(producer(),), horizon=1))
        self.assertEqual(p.decision.kind, "abstain")

    def test_repair_forecast_is_target_specific(self):
        p = plan_joint_archive(
            seeded((A, B)), (REP,),
            model(priors=((A, .1, "bad"), (B, .1, "good")),
                  kernels=(),
                  producers=(
                      producer("rep", "repair", "bad", (),
                               (ProducerOutcome(1, .99, "fresh"),)),
                      producer("rep", "repair", "good", (),
                               (ProducerOutcome(1, .2, "fresh"),)),
                  ), horizon=1))
        self.assertEqual((p.decision.action_id, p.decision.target_sha256),
                         ("rep", A))

    def test_record_repair_preserves_parent_and_ancestry(self):
        inputs = model(
            priors=((A, .1, "bad"),), kernels=(),
            producers=(producer("rep", "repair", "bad", (),
                                (ProducerOutcome(1, .99, "fresh"),)),),
            horizon=1)
        s = seeded()
        d = plan_joint_archive(s, (REP,), inputs).decision
        after = record_joint_archive(
            s, (REP,), inputs, d, reported_cost=REP.cost,
            new_candidate_sha256=B)
        self.assertEqual([c.sha256 for c in after.state.candidates], [A, B])
        self.assertEqual(after.state.candidates[1].parent_sha256, A)
        self.assertEqual(after.state.observations, ())

    def test_diagnostic_only_changes_its_own_patch(self):
        inputs = model(priors=((A, .5, "base"), (B, .5, "base")), horizon=1)
        s = seeded((A, B))
        d = plan_joint_archive(s, (TEST,), inputs).decision
        self.assertEqual(d.target_sha256, A)
        after = record_joint_archive(
            s, (TEST,), inputs, d, reported_cost=TEST.cost,
            observed_positive=False)
        self.assertEqual(after.state.observations[0].candidate_sha256, A)
        # B remains untested; a new globally unused test can target B.
        next_plan = plan_joint_archive(
            after, (TEST, TEST2),
            model(priors=((A, .5, "base"), (B, .5, "base")),
                  kernels=(("base", ConditionalKernel(PERFECT.rows + (
                      ConditionalRow("test2", (Observation("test", False),),
                                     .5, .5),))),),
                  horizon=1))
        self.assertEqual((next_plan.decision.action_id,
                          next_plan.decision.target_sha256), ("test2", B))

    def test_missing_root_diagnostic_kernel_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing frozen kernel"):
            plan_joint_archive(seeded(), (TEST,), model(kernels=()))

    def test_missing_root_producer_forecast_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing target-conditioned"):
            plan_joint_archive(seeded(()), (GEN,), model(priors=(), kernels=()))

    def test_missing_target_specific_repair_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing target-conditioned"):
            plan_joint_archive(
                seeded((A, B)), (REP,),
                model(priors=((A, .1, "bad"), (B, .1, "good")),
                      kernels=(),
                      producers=(producer("rep", "repair", "bad", ()),),
                      horizon=1))

    def test_missing_future_child_kernel_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing frozen kernel"):
            plan_joint_archive(
                seeded(()), (GEN, TEST),
                model(priors=(), kernels=(), producers=(producer(),), horizon=2))

    def test_global_one_use_test_id(self):
        s = seeded()
        d = plan_joint_archive(s, (TEST,), model(horizon=1)).decision
        after = record_joint_archive(
            s, (TEST,), model(horizon=1), d,
            reported_cost=TEST.cost, observed_positive=True)
        p = plan_joint_archive(after, (TEST,), model(horizon=2))
        self.assertEqual((p.decision.kind, p.decision.target_sha256),
                         ("release", A))

    def test_generation_failure_still_spends_shared_budget(self):
        s = seeded(())
        d = SharedDecision("gen", "generate", None, GEN.cost)
        after = commit_shared(s, (GEN,), d, reported_cost=GEN.cost)
        self.assertEqual(after.state.remaining.tokens, 4)
        self.assertEqual(after.state.candidates, ())

    def test_symbolic_key_cannot_be_real_candidate(self):
        sym = SymbolicCandidateKey("gen", 0)
        with self.assertRaisesRegex(ValueError, "SHA256"):
            commit_shared(
                seeded(()), (GEN,),
                SharedDecision("gen", "generate", None, GEN.cost),
                reported_cost=GEN.cost, new_candidate_sha256=sym)

    def test_initial_belief_coverage_is_exact(self):
        with self.assertRaisesRegex(ValueError, "exactly match"):
            plan_joint_archive(seeded(), (TEST,), model(priors=()))

    def test_producer_probabilities_must_sum_to_one(self):
        with self.assertRaisesRegex(ValueError, "sum to one"):
            producer(outcomes=(ProducerOutcome(.6, .9, "fresh"),))

    def test_generate_must_be_target_free_in_forecast(self):
        with self.assertRaisesRegex(ValueError, "target-free"):
            producer(profile="base")

    def test_duplicate_profile_forecast_rejected(self):
        f = producer()
        with self.assertRaisesRegex(ValueError, "duplicate target"):
            model(priors=(), producers=(f, f))

    def test_model_has_no_hidden_oracle_label_field(self):
        self.assertFalse(any(x in FrozenJointInputs.__dataclass_fields__
                             for x in ("gold", "oracle", "hidden_test", "label")))

    def test_state_expansion_cap_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "state cap"):
            plan_joint_archive(seeded(), (TEST,), model(max_states=1))

    def test_action_catalog_order_invariant(self):
        inputs = model(horizon=1)
        a = plan_joint_archive(seeded(), (TEST, TEST2), inputs)
        b = plan_joint_archive(seeded(), (TEST2, TEST), inputs)
        self.assertEqual((a.decision, a.expected_proxy_utility),
                         (b.decision, b.expected_proxy_utility))

    def test_cost_can_reverse_positive_information_value(self):
        p = plan_joint_archive(
            seeded(), (TEST,),
            model(horizon=1, prices=ResourcePrices(test_calls=2)))
        self.assertEqual(p.decision.kind, "abstain")

    def test_existing_history_requires_exact_conditional_row(self):
        s = commit_shared(
            seeded(), (TEST,),
            SharedDecision("test", "test", A, TEST.cost),
            reported_cost=TEST.cost, observed_positive=True)
        # Another diagnostic requires a kernel row conditioned on the exact
        # previously visible test outcome; the empty-history row is insufficient.
        with self.assertRaisesRegex(ValueError, "missing frozen conditional"):
            plan_joint_archive(
                s, (TEST, TEST2), model(horizon=1))


if __name__ == "__main__":
    unittest.main()
