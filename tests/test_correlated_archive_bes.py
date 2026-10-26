"""SYNTHETIC correlation-aware archive planning falsifiers, never RQ results."""
from dataclasses import replace
import unittest

from ucode.conditional_bes import ConditionalKernel, ConditionalRow, Observation
from ucode.correlated_archive_bes import (
    CandidateProfile, CorrelatedPlan, CorrelatedProducerRow, FrozenCorrelatedInputs, TruthAtom,
    _posterior_branch, _producer_branches, plan_correlated_archive,
    record_correlated_archive,
    public_producer_trace_sha256,
)
from ucode.matched_session import SharedDecision, SharedSession, commit_shared
from ucode.optimized_search import SearchAction, SearchCandidate, SearchState
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule

A, B, C = "a"*64, "b"*64, "c"*64
BUDGET = ResourceVector(tokens=5, test_calls=2, cpu_seconds=2)
TEST = SearchAction("test", "test", ResourceVector(test_calls=1))
TEST2 = SearchAction("test2", "test", ResourceVector(test_calls=1))
GEN = SearchAction("gen", "generate", ResourceVector(tokens=1))
REP = SearchAction("rep", "repair", ResourceVector(tokens=1))
PERFECT = ConditionalKernel((
    ConditionalRow("test", (), 1, 0),
    ConditionalRow("test2", (), 1, 0),
))
HALF = ConditionalKernel((ConditionalRow("test", (), .5, .5),))


def seeded(keys=(A,), cap=8):
    return SharedSession(
        BUDGET,
        SearchState(BUDGET, tuple(SearchCandidate(x, "initial") for x in keys),
                    keys[0] if keys else None),
        max_candidates=cap)


def truth(*bits, mass=1):
    return TruthAtom(tuple(bits), mass)


def frozen(keys=(A,), atoms=None, kernels=(("base", PERFECT),),
           producers=(), horizon=2, max_states=30000, max_atoms=256,
           prices=ResourcePrices()):
    if atoms is None:
        atoms = (truth(*([False]*len(keys)), mass=.5),
                 truth(*([True]*len(keys)), mass=.5))
    return FrozenCorrelatedInputs(
        tuple(CandidateProfile(k, "base") for k in keys), tuple(atoms),
        kernels, tuple(producers), prices,
        ReleaseRule(max_predicted_failure=.1), horizon,
        max_states, max_atoms)


def producer(action="gen", kind="generate", target=None, history=(),
             produced_true=1, produced_false=1, child_true=0.5,
             child_false=0.5, profile="base"):
    return CorrelatedProducerRow(
        action, kind, target, history,
        produced_true, produced_false, child_true, child_false, profile)


class CorrelatedArchiveTests(unittest.TestCase):
    def test_positive_evidence_updates_correlated_sibling(self):
        s = commit_shared(
            seeded((A, B)), (TEST,),
            SharedDecision("test", "test", A, TEST.cost),
            reported_cost=TEST.cost, observed_positive=True)
        plan = plan_correlated_archive(
            s, (TEST,), frozen(keys=(A, B)))
        self.assertEqual(plan.posterior_marginals, ((A, 1.0), (B, 1.0)))
        self.assertEqual(plan.decision.kind, "release")

    def test_negative_evidence_updates_correlated_sibling(self):
        s = commit_shared(
            seeded((A, B)), (TEST,),
            SharedDecision("test", "test", A, TEST.cost),
            reported_cost=TEST.cost, observed_positive=False)
        plan = plan_correlated_archive(s, (TEST,), frozen(keys=(A, B)))
        self.assertEqual(plan.posterior_marginals, ((A, 0.0), (B, 0.0)))
        self.assertEqual(plan.decision.kind, "abstain")

    def test_anti_correlated_sibling_moves_opposite(self):
        s = commit_shared(
            seeded((A, B)), (TEST,),
            SharedDecision("test", "test", A, TEST.cost),
            reported_cost=TEST.cost, observed_positive=True)
        atoms = (truth(False, True, mass=.5),
                 truth(True, False, mass=.5))
        p = plan_correlated_archive(
            s, (TEST,), frozen(keys=(A, B), atoms=atoms))
        self.assertEqual(p.posterior_marginals, ((A, 1.0), (B, 0.0)))

    def test_independent_prior_leaves_sibling_unchanged(self):
        s = commit_shared(
            seeded((A, B)), (TEST,),
            SharedDecision("test", "test", A, TEST.cost),
            reported_cost=TEST.cost, observed_positive=True)
        atoms = tuple(truth(a, b, mass=.25)
                      for a in (False, True) for b in (False, True))
        p = plan_correlated_archive(
            s, (TEST,), frozen(keys=(A, B), atoms=atoms))
        self.assertEqual(p.posterior_marginals, ((A, 1.0), (B, .5)))

    def test_positive_evidence_can_release_other_patch(self):
        s = commit_shared(
            seeded((A, B)), (TEST,),
            SharedDecision("test", "test", A, TEST.cost),
            reported_cost=TEST.cost, observed_positive=True)
        atoms = (truth(False, False, mass=.5),
                 truth(True, True, mass=.5))
        p = plan_correlated_archive(
            s, (TEST,), frozen(keys=(A, B), atoms=atoms))
        self.assertEqual(p.decision.target_sha256, A)
        self.assertEqual(p.posterior_marginals[1][1], 1)

    def test_same_marginals_different_correlation_reverses_action(self):
        # Synthetic controlled counterexample: A and C are anticorrelated,
        # while B is independent. Under an independent prior the perfect
        # B-specific probe wins; under the anticorrelated prior the noisy
        # A/C probe can identify a releasable candidate in BOTH branches.
        probe_a = SearchAction("probe_a", "test",
                               ResourceVector(test_calls=1))
        probe_b = SearchAction("probe_b", "test",
                               ResourceVector(test_calls=1))
        weak = ConditionalKernel((
            ConditionalRow("probe_a", (), .95, .05),
            ConditionalRow("probe_b", (), .5, .5),
        ))
        strong = ConditionalKernel((
            ConditionalRow("probe_a", (), .5, .5),
            ConditionalRow("probe_b", (), 1, 0),
        ))
        profiles = (CandidateProfile(A, "weak"),
                    CandidateProfile(B, "strong"),
                    CandidateProfile(C, "weak"))
        anticorrelated = tuple(
            truth(a, b, not a, mass=.25)
            for a in (False, True) for b in (False, True))
        independent = tuple(
            truth(a, b, c, mass=.125)
            for a in (False, True)
            for b in (False, True)
            for c in (False, True))
        def inputs(atoms):
            return FrozenCorrelatedInputs(
                profiles, atoms, (("weak", weak), ("strong", strong)),
                horizon=1)
        s = seeded((A, B, C))
        p_corr = plan_correlated_archive(
            s, (probe_a, probe_b), inputs(anticorrelated))
        p_ind = plan_correlated_archive(
            s, (probe_a, probe_b), inputs(independent))
        self.assertEqual(p_corr.posterior_marginals,
                         p_ind.posterior_marginals)
        self.assertEqual((p_corr.decision.action_id,
                          p_corr.decision.target_sha256), ("probe_a", A))
        self.assertEqual((p_ind.decision.action_id,
                          p_ind.decision.target_sha256), ("probe_b", B))
        self.assertAlmostEqual(p_corr.expected_proxy_utility, .9)
        self.assertAlmostEqual(p_ind.expected_proxy_utility, .5)

    def test_root_one_step_positive_voi(self):
        p = plan_correlated_archive(seeded(), (TEST,), frozen(horizon=1))
        self.assertEqual((p.decision.action_id, p.decision.target_sha256),
                         ("test", A))
        self.assertGreater(p.expected_proxy_utility, p.stop_utility)

    def test_root_diagnostic_target_tie_is_deterministic(self):
        p = plan_correlated_archive(
            seeded((A, B)), (TEST,), frozen(keys=(A, B), horizon=1))
        self.assertEqual(p.decision.target_sha256, A)

    def test_action_order_does_not_change_result(self):
        inp = frozen(horizon=1)
        p = plan_correlated_archive(seeded(), (TEST, TEST2), inp)
        q = plan_correlated_archive(seeded(), (TEST2, TEST), inp)
        self.assertEqual((p.decision, p.expected_proxy_utility),
                         (q.decision, q.expected_proxy_utility))

    def test_cost_can_reverse_voi(self):
        p = plan_correlated_archive(
            seeded(), (TEST,),
            frozen(horizon=1, prices=ResourcePrices(test_calls=2)))
        self.assertEqual(p.decision.kind, "abstain")

    def test_diagnostic_receipt_rejects_unselected_action(self):
        s = seeded()
        inp = frozen(horizon=1)
        selected = plan_correlated_archive(s, (TEST,), inp).decision
        with self.assertRaisesRegex(ValueError, "unselected"):
            record_correlated_archive(
                s, (TEST,), inp, replace(selected, target_sha256=B),
                reported_cost=TEST.cost, observed_positive=True)

    def test_diagnostic_receipt_is_policy_visible_only(self):
        s = seeded()
        inp = frozen(horizon=1)
        d = plan_correlated_archive(s, (TEST,), inp).decision
        after = record_correlated_archive(
            s, (TEST,), inp, d,
            reported_cost=TEST.cost, observed_positive=True)
        self.assertEqual(after.state.observations[0].candidate_sha256, A)
        self.assertEqual(len(after.receipts), 1)

    def test_impossible_visible_history_fails_closed(self):
        s = commit_shared(
            seeded(), (TEST,),
            SharedDecision("test", "test", A, TEST.cost),
            reported_cost=TEST.cost, observed_positive=True)
        with self.assertRaisesRegex(ValueError, "zero probability"):
            plan_correlated_archive(
                s, (TEST,), frozen(atoms=(truth(False),)))

    def test_missing_kernel_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing frozen kernel"):
            plan_correlated_archive(
                seeded(), (TEST,), frozen(kernels=(), horizon=1))

    def test_missing_conditional_history_fails_closed(self):
        s = commit_shared(
            seeded(), (TEST,),
            SharedDecision("test", "test", A, TEST.cost),
            reported_cost=TEST.cost, observed_positive=True)
        with self.assertRaisesRegex(ValueError, "missing frozen conditional"):
            plan_correlated_archive(s, (TEST, TEST2), frozen(horizon=1))

    def test_future_generation_then_test(self):
        inp = frozen(keys=(), atoms=(truth(),),
                     producers=(producer(),), horizon=2)
        p = plan_correlated_archive(seeded(()), (GEN, TEST), inp)
        self.assertEqual((p.decision.action_id, p.decision.target_sha256),
                         ("gen", None))
        self.assertGreater(p.expected_proxy_utility, 0)

    def test_generator_failure_no_benefit(self):
        inp = frozen(keys=(), atoms=(truth(),), kernels=(),
                     producers=(producer(produced_true=0,
                                         produced_false=0),), horizon=2)
        p = plan_correlated_archive(seeded(()), (GEN,), inp)
        self.assertEqual(p.decision.kind, "abstain")

    def test_repair_truth_dependent_child_creation(self):
        # Repairing a certainly unacceptable parent deterministically
        # creates a new acceptable child in this *hypothetical* model.
        inp = frozen(atoms=(truth(False),), kernels=(),
                     producers=(producer(
                         "rep", "repair", "base",
                         child_true=0, child_false=1),), horizon=1)
        p = plan_correlated_archive(seeded(), (REP,), inp)
        self.assertEqual((p.decision.action_id, p.decision.target_sha256),
                         ("rep", A))
        self.assertEqual(p.expected_proxy_utility, 1)

    def test_failed_repair_is_information_about_sibling(self):
        atoms = (truth(False, False, mass=.5),
                 truth(True, True, mass=.5))
        row = producer("rep", "repair", "base",
                       produced_true=.9, produced_false=.1)
        failure, success = _producer_branches(atoms, 0, row, 8)
        self.assertAlmostEqual(failure[0], .5)
        self.assertAlmostEqual(success[0], .5)
        self.assertAlmostEqual(
            sum(a.probability for a in failure[1] if a.bits[1]), .1)
        self.assertAlmostEqual(
            sum(a.probability for a in success[1] if a.bits[1]), .9)

    def test_produced_child_correlates_with_parent(self):
        atoms = (truth(False, mass=.5), truth(True, mass=.5))
        row = producer("rep", "repair", "base",
                       child_true=1, child_false=0)
        failure, success = _producer_branches(atoms, 0, row, 8)
        self.assertEqual(failure[0], 0)
        self.assertAlmostEqual(success[0], 1)
        self.assertTrue(all(a.bits[0] == a.bits[1] for a in success[1]))

    def test_joint_bayes_update_obeys_marginal_martingale(self):
        # The expected posterior of a sibling must equal its prior
        # before the diagnostic outcome is observed.
        atoms = (truth(False, True, mass=.5),
                 truth(True, False, mass=.5))
        row = ConditionalRow("test", (), .8, .2)
        positive, pos = _posterior_branch(atoms, 0, row, True, 8)
        negative, neg = _posterior_branch(atoms, 0, row, False, 8)
        expected_b = (
            positive * sum(a.probability for a in pos if a.bits[1])
            + negative * sum(a.probability for a in neg if a.bits[1]))
        self.assertAlmostEqual(positive+negative, 1)
        self.assertAlmostEqual(expected_b, .5)

    def test_producer_observation_obeys_parent_martingale(self):
        atoms = (truth(False, mass=.5), truth(True, mass=.5))
        row = producer("rep", "repair", "base",
                       produced_true=.9, produced_false=.1,
                       child_true=.8, child_false=.2)
        failure, success = _producer_branches(atoms, 0, row, 8)
        expected_parent = (
            failure[0] * sum(a.probability for a in failure[1] if a.bits[0])
            + success[0] * sum(a.probability for a in success[1] if a.bits[0]))
        self.assertAlmostEqual(failure[0]+success[0], 1)
        self.assertAlmostEqual(expected_parent, .5)

    def test_generator_does_not_condition_existing_truth(self):
        atoms = (truth(False, mass=.3), truth(True, mass=.7))
        row = producer(produced_true=.6, produced_false=.6,
                       child_true=.2, child_false=.2)
        failure, success = _producer_branches(atoms, None, row, 8)
        self.assertAlmostEqual(failure[0], .4)
        self.assertAlmostEqual(success[0], .6)
        self.assertAlmostEqual(
            sum(a.probability for a in success[1] if a.bits[0]), .7)
        self.assertAlmostEqual(
            sum(a.probability for a in success[1] if a.bits[1]), .2)

    def test_production_support_cap_fails_closed(self):
        inp = frozen(keys=(), atoms=(truth(),), kernels=(),
                     producers=(producer(),), horizon=1, max_atoms=1)
        with self.assertRaisesRegex(ValueError, "atom cap"):
            plan_correlated_archive(seeded(()), (GEN,), inp)

    def test_missing_generator_forecast_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing target-conditioned"):
            plan_correlated_archive(
                seeded(()), (GEN,), frozen(keys=(), atoms=(truth(),),
                                           kernels=(), horizon=1))

    def test_missing_future_child_kernel_fails_closed(self):
        inp = frozen(keys=(), atoms=(truth(),), kernels=(),
                     producers=(producer(),), horizon=2)
        with self.assertRaisesRegex(ValueError, "missing frozen kernel"):
            plan_correlated_archive(seeded(()), (GEN, TEST), inp)

    def test_repair_requires_target_profile_forecast(self):
        with self.assertRaisesRegex(ValueError, "missing target-conditioned"):
            plan_correlated_archive(seeded(), (REP,), frozen(horizon=1))

    def test_joint_prior_width_rejected(self):
        with self.assertRaisesRegex(ValueError, "profile width"):
            frozen(keys=(A, B), atoms=(truth(False),))

    def test_joint_prior_sum_rejected(self):
        with self.assertRaisesRegex(ValueError, "sum to one"):
            frozen(atoms=(truth(False, mass=.3),
                          truth(True, mass=.3)))

    def test_duplicate_atoms_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique typed joint"):
            frozen(atoms=(truth(False, mass=.5),
                          truth(False, mass=.5)))

    def test_unsorted_profiles_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA-sorted"):
            frozen(keys=(B, A))

    def test_target_free_generator_cannot_depend_on_hidden_parent(self):
        with self.assertRaisesRegex(ValueError, "truth-independent"):
            producer(produced_true=.8, produced_false=.2)

    def test_failed_real_production_requires_explicit_prior_binding(self):
        s = commit_shared(
            seeded(), (REP,),
            SharedDecision("rep", "repair", A, REP.cost),
            reported_cost=REP.cost)
        with self.assertRaisesRegex(ValueError, "producer-history binding"):
            plan_correlated_archive(s, (REP,), frozen())
        # The digest binds an externally supplied prior to the public
        # producer history; it does NOT independently certify calibration.
        inp = replace(
            frozen(),
            conditioned_on_producer_receipts_sha256=public_producer_trace_sha256(s))
        p = plan_correlated_archive(s, (REP,), inp)
        self.assertEqual(p.decision.kind, "abstain")

    def test_producer_binding_changes_with_visible_outcome(self):
        failed = commit_shared(
            seeded(), (REP,),
            SharedDecision("rep", "repair", A, REP.cost),
            reported_cost=REP.cost)
        produced = commit_shared(
            seeded(), (REP,),
            SharedDecision("rep", "repair", A, REP.cost),
            reported_cost=REP.cost, new_candidate_sha256=B)
        self.assertNotEqual(public_producer_trace_sha256(failed),
                            public_producer_trace_sha256(produced))

    def test_produced_real_patch_requires_new_joint_profile(self):
        after = commit_shared(
            seeded(), (REP,),
            SharedDecision("rep", "repair", A, REP.cost),
            reported_cost=REP.cost, new_candidate_sha256=B)
        inp = replace(
            frozen(),
            conditioned_on_producer_receipts_sha256=public_producer_trace_sha256(after))
        with self.assertRaisesRegex(ValueError, "exactly match"):
            plan_correlated_archive(after, (REP,), inp)

    def test_producer_binding_rejects_invalid_digest(self):
        with self.assertRaisesRegex(ValueError, "requires SHA256"):
            replace(frozen(), conditioned_on_producer_receipts_sha256="bad")

    def test_missing_archive_profile_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly match"):
            plan_correlated_archive(
                seeded((A, B)), (TEST,), frozen(keys=(A,)))

    def test_state_cap_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "state cap"):
            plan_correlated_archive(
                seeded(), (TEST,), frozen(max_states=1))

    def test_excessive_archive_cap_rejected(self):
        with self.assertRaisesRegex(ValueError, "archive cap"):
            plan_correlated_archive(
                seeded(cap=9), (TEST,), frozen())

    def test_zero_candidate_terminal_abstains(self):
        p = plan_correlated_archive(
            seeded(()), (), frozen(keys=(), atoms=(truth(),)))
        self.assertEqual(p.decision.kind, "abstain")

    def test_no_oracle_in_public_contract(self):
        forbidden = {"oracle", "gold", "hidden_test", "true_labels"}
        self.assertFalse(forbidden & set(FrozenCorrelatedInputs.__dataclass_fields__))
        self.assertFalse(forbidden & set(CorrelatedPlan.__dataclass_fields__))


if __name__ == "__main__":
    unittest.main()
