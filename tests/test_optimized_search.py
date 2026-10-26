"""SYNTHETIC tests only: no LLM, external repository, or independent oracle."""
from dataclasses import replace
import unittest

from ucode.optimized_search import (
    SearchAction, SearchCandidate, SearchDecision, SearchObservation,
    SearchPolicy, SearchState, choose_search, record_search,
    search_catalog_from_public_manifest,
)
from ucode.vector_policy import RESOURCE_FIELDS, ResourcePrices, ResourceVector

A, B, C = "a" * 64, "b" * 64, "c" * 64


def fixture():
    return (
        SearchAction("gen", "generate", ResourceVector(tokens=5)),
        SearchAction("gen2", "generate", ResourceVector(tokens=7)),
        SearchAction("test", "test", ResourceVector(test_calls=1)),
        SearchAction("test2", "test", ResourceVector(test_calls=1)),
        SearchAction("repair", "repair", ResourceVector(tokens=3)),
        SearchAction("static", "static_analysis", ResourceVector(cpu_seconds=2)),
        SearchAction("retrieve", "retrieve", ResourceVector(tokens=1)),
    )


def policy(**kwargs):
    return SearchPolicy(**kwargs)


def initial(**kwargs):
    return SearchState(ResourceVector(tokens=30, test_calls=3,
                                      cpu_seconds=5, gpu_seconds=2,
                                      wall_seconds=40), **kwargs)


class OptimizedSearchTests(unittest.TestCase):
    def test_beam_is_not_fixed_schedule_and_is_permutation_invariant(self):
        ac = (
            SearchAction("expensive", "generate", ResourceVector(tokens=8)),
            SearchAction("cheap", "generate", ResourceVector(tokens=2)),
            SearchAction("test", "test", ResourceVector(test_calls=1)),
        )
        p = policy(depth=2, resource_prices=ResourcePrices(tokens=0.5))
        s = initial()
        self.assertEqual(choose_search(s, ac, p).action, "cheap")
        self.assertEqual(choose_search(s, ac[::-1], p), choose_search(s, ac, p))
        self.assertGreater(choose_search(s, ac, p).states_expanded, 1)

    def test_generate_then_visible_test_then_release(self):
        ac = (
            SearchAction("g", "generate", ResourceVector(tokens=2)),
            SearchAction("t", "test", ResourceVector(test_calls=1)),
        )
        s = initial()
        d = choose_search(s, ac)
        self.assertEqual(d.action, "g")
        s = record_search(s, ac, d, new_candidate_sha256=A)
        self.assertEqual((s.candidates[0].sha256, s.active_sha256), (A, A))
        self.assertEqual(choose_search(s, ac).action, "t")
        s = record_search(s, ac, choose_search(s, ac), observed_positive=True)
        d = choose_search(s, ac)
        self.assertEqual((d.action, d.candidate_sha256), ("release", A))
        self.assertEqual(s.remaining.tokens, 28)
        self.assertEqual(s.remaining.test_calls, 2)

    def test_negative_test_and_repair_keep_stale_evidence_attached_to_parent(self):
        ac = (
            SearchAction("g", "generate", ResourceVector(tokens=2)),
            SearchAction("test", "test", ResourceVector(test_calls=1)),
            SearchAction("repair", "repair", ResourceVector(tokens=3)),
            SearchAction("retest", "test", ResourceVector(test_calls=1)),
        )
        s = initial()
        s = record_search(s, ac, choose_search(s, ac), new_candidate_sha256=A)
        # At this point the controller can plan tests or repair. Freeze a
        # test-first configuration for this engineering counterexample.
        p = policy(action_rewards=(0, 1, 10, 0, 0), depth=1)
        s = record_search(s, ac, choose_search(s, ac, p),
                          observed_positive=False, policy=p)
        self.assertEqual(choose_search(s, ac, policy(depth=1)).kind, "repair")
        d = choose_search(s, ac, policy(depth=1))
        s = record_search(s, ac, d, new_candidate_sha256=B,
                          policy=policy(depth=1))
        self.assertEqual(s.candidates[-1].parent_sha256, A)
        self.assertEqual((s.observations[0].candidate_sha256, s.active_sha256),
                         (A, B))
        self.assertFalse(any(o.candidate_sha256 == B for o in s.observations))
        self.assertEqual(s.remaining.tokens, 25)

    def test_failed_candidate_generation_consumes_budget_without_forging_patch(self):
        ac = (SearchAction("g", "generate", ResourceVector(tokens=4)),)
        s = record_search(initial(), ac, choose_search(initial(), ac),
                          new_candidate_sha256=None)
        self.assertEqual((s.candidates, s.attempted), ((), ("g",)))
        self.assertEqual(s.remaining.tokens, 26)
        self.assertEqual(choose_search(s, ac).action, "abstain")

    def test_distinct_archive_candidates_survive_and_old_candidate_can_release(self):
        ac = (
            SearchAction("g", "generate", ResourceVector(tokens=2)),
            SearchAction("g2", "generate", ResourceVector(tokens=2)),
            SearchAction("t", "test", ResourceVector(test_calls=1)),
        )
        p = policy(depth=1, action_rewards=(10, 1, 1, 0, 0))
        s = record_search(initial(), ac, choose_search(initial(), ac, p),
                          new_candidate_sha256=A, policy=p)
        # Pre-existing evidence is allowed only if bound to an executed
        # diagnostic action and the same SHA (archive persists).
        s = replace(s, attempted=s.attempted + ("t",),
                    observations=(SearchObservation("t", A, "test", True),))
        s = record_search(s, ac, choose_search(s, ac, p),
                          new_candidate_sha256=B, policy=p)
        self.assertEqual(len(s.candidates), 2)
        self.assertEqual(s.candidates[-1].parent_sha256, None)
        self.assertEqual(choose_search(s, ac, p).action, "release")
        self.assertEqual(choose_search(s, ac, p).candidate_sha256, A)

    def test_archive_capacity_is_hard(self):
        ac = (SearchAction("g", "generate", ResourceVector(tokens=1)),
              SearchAction("g2", "generate", ResourceVector(tokens=1)))
        p = policy(max_candidates=1)
        s = record_search(initial(), ac, choose_search(initial(), ac, p),
                          new_candidate_sha256=A, policy=p)
        self.assertEqual(choose_search(s, ac, p).action, "abstain")

    def test_all_five_budget_dimensions_individually_block(self):
        for key in RESOURCE_FIELDS:
            with self.subTest(resource=key):
                cost = ResourceVector(**{key: 1})
                a = SearchAction("g", "generate", cost)
                self.assertEqual(choose_search(
                    SearchState(ResourceVector()), (a,)).action, "abstain")
                self.assertEqual(choose_search(
                    SearchState(cost), (a,)).action, "g")

    def test_reject_oracle_and_probability_fields_in_action_manifest(self):
        row = {"action_id": "g", "kind": "generate",
               "cost": ResourceVector(tokens=2).__dict__}
        self.assertEqual(search_catalog_from_public_manifest([row])[0].action_id, "g")
        for key in ("posterior", "prior", "confidence", "predicted_success",
                    "sensitivity", "oracle_passed", "gold_patch", "risk",
                    "hidden_tests", "expected_terminal_value_after"):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "leakage"):
                search_catalog_from_public_manifest([{**row, key: 0.9}])

    def test_missing_cost_vector_rejected(self):
        with self.assertRaisesRegex(ValueError, "five budget"):
            search_catalog_from_public_manifest([
                {"action_id": "g", "kind": "generate", "cost": {"tokens": 2}}
            ])

    def test_typed_state_has_no_oracle_or_uncertainty_features(self):
        forbidden = {"prior", "posterior", "sensitivity", "specificity",
                     "gold", "oracle_passed", "predicted_success"}
        for c in (SearchAction, SearchCandidate, SearchState, SearchObservation):
            self.assertFalse(set(c.__dataclass_fields__) & forbidden)

    def test_bad_configurations_fail_closed(self):
        with self.assertRaises(ValueError):
            policy(depth=0)
        with self.assertRaises(ValueError):
            policy(beam_width=100)
        with self.assertRaises(ValueError):
            policy(action_rewards=(1, 2))
        with self.assertRaises(ValueError):
            policy(first_test_bonus=float("nan"))
        with self.assertRaises(ValueError):
            policy(max_candidates=True)
        with self.assertRaises(ValueError):
            policy(min_positive_tests=0)

    def test_duplicate_action_id_and_archive_candidate_refused(self):
        g = fixture()[0]
        with self.assertRaisesRegex(ValueError, "duplicate action"):
            choose_search(initial(), (g, g))
        with self.assertRaisesRegex(ValueError, "duplicate candidate"):
            SearchState(ResourceVector(), (SearchCandidate(A, "initial"),
                                            SearchCandidate(A, "initial")), A)
        s = initial()
        with self.assertRaisesRegex(ValueError, "duplicate/replayed"):
            ac = (g,)
            record_search(SearchState(s.remaining, (SearchCandidate(A,"initial"),), A),
                          ac, choose_search(SearchState(s.remaining,
                            (SearchCandidate(A,"initial"),), A), ac),
                          new_candidate_sha256=A)

    def test_bad_stale_or_unbound_observation_refused(self):
        with self.assertRaisesRegex(ValueError, "unseen"):
            SearchState(ResourceVector(), (SearchCandidate(B, "initial"),),
                        B, ("t",), (SearchObservation("t", A, "test", True),))
        with self.assertRaisesRegex(ValueError, "unseen"):
            SearchState(ResourceVector(), (SearchCandidate(B, "initial"),),
                        B, (), (SearchObservation("t", B, "test", True),))

    def test_negative_result_is_not_hidden_oracle_pass(self):
        ac = (SearchAction("g", "generate", ResourceVector(tokens=2)),
              SearchAction("t", "test", ResourceVector(test_calls=1)))
        s = record_search(initial(), ac, choose_search(initial(), ac),
                          new_candidate_sha256=A)
        p = policy(depth=1)
        d = choose_search(s, ac, p)
        self.assertEqual(d.kind, "test")
        for outcome in (0, "pass"):
            with self.subTest(outcome=outcome), self.assertRaises(ValueError):
                record_search(s, ac, d, observed_positive=outcome, policy=p)
        with self.assertRaises(ValueError):
            record_search(s, ac, d, observed_positive=True,
                          new_candidate_sha256=B, policy=p)
        s = record_search(s, ac, d, observed_positive=False, policy=p)
        self.assertEqual(choose_search(s, ac).action, "abstain")

    def test_reject_forged_decision_and_exogenous_oracle(self):
        ac = (SearchAction("g", "generate", ResourceVector(tokens=2)),)
        s = initial()
        d = choose_search(s, ac)
        with self.assertRaisesRegex(ValueError, "unselected"):
            record_search(s, ac, replace(d, budget_after_first=s.remaining),
                          new_candidate_sha256=A)
        with self.assertRaisesRegex(ValueError, "oracle"):
            record_search(s, ac, d, observed_positive=True,
                          new_candidate_sha256=A)
        with self.assertRaisesRegex(ValueError, "terminal"):
            record_search(SearchState(ResourceVector()), ac,
                          choose_search(SearchState(ResourceVector()), ac))

    def test_realized_cost_is_not_claimed_by_nominal_charge(self):
        # This counterexample documents the scope: the record module checks
        # declared cost; actual GPU/CPU/wall telemetry requires a gated runner.
        ac = (SearchAction("g", "generate",
                           ResourceVector(tokens=2, wall_seconds=1)),)
        s = record_search(initial(), ac, choose_search(initial(), ac),
                          new_candidate_sha256=A)
        self.assertEqual(s.remaining.wall_seconds, 39)
        self.assertNotIn("measured_cost", SearchState.__dataclass_fields__)

    def test_absent_tool_and_mismatched_provenance_rejected(self):
        ac = (SearchAction("g", "generate", ResourceVector(tokens=1)),)
        s = initial(attempted=("imaginary",))
        with self.assertRaisesRegex(ValueError, "absent"):
            choose_search(s, ac)
        with self.assertRaisesRegex(ValueError, "origin"):
            choose_search(initial(candidates=(SearchCandidate(A,"t"),),
                                         active_sha256=A,attempted=("t",)),
                          (SearchAction("t","test",ResourceVector(test_calls=1)),))

    def test_wrong_cost_or_nonfinite_vector_fails(self):
        with self.assertRaises(ValueError):
            SearchAction("x", "generate", ResourceVector())
        with self.assertRaises(ValueError):
            ResourceVector(wall_seconds=float("inf"))


    def test_generation_action_cannot_claim_two_different_patches(self):
        with self.assertRaisesRegex(ValueError, "two artifacts"):
            SearchState(
                ResourceVector(tokens=1),
                (SearchCandidate(A, "g"), SearchCandidate(B, "g")),
                B, ("g",),
            )

    def test_diagnostic_cannot_precede_candidate_in_attempt_chronology(self):
        with self.assertRaisesRegex(ValueError, "predates candidate"):
            SearchState(
                ResourceVector(), (SearchCandidate(A, "g"),), A,
                ("test", "g"), (SearchObservation("test", A, "test", True),),
            )

    def test_repair_cannot_precede_parent_generation(self):
        with self.assertRaisesRegex(ValueError, "precede parent"):
            SearchState(
                ResourceVector(),
                (SearchCandidate(A, "g"), SearchCandidate(B, "repair", A)),
                B, ("repair", "g"),
            )

    def test_visible_diagnostics_must_follow_attempt_order(self):
        with self.assertRaisesRegex(ValueError, "chronology"):
            SearchState(
                ResourceVector(), (SearchCandidate(A, "initial"),), A,
                ("first", "second"),
                (SearchObservation("second", A, "test", True),
                 SearchObservation("first", A, "test", False)),
            )


if __name__ == "__main__":
    unittest.main()
