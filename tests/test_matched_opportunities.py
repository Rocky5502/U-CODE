"""SYNTHETIC adversarial tests for policy-neutral action-target parity."""
from dataclasses import replace
import unittest

from ucode.matched_opportunities import (
    Opportunity, choose_matched_baseline, matched_opportunities,
    opportunity_digest, record_matched_baseline,
)
from ucode.matched_session import SharedDecision, SharedSession, commit_shared
from ucode.optimized_search import (
    SearchAction, SearchCandidate, SearchObservation, SearchPolicy, SearchState,
)
from ucode.vector_policy import RESOURCE_FIELDS, ResourceVector

A, B = "a"*64, "b"*64
CAP = ResourceVector(tokens=8, test_calls=2, gpu_seconds=2,
                     cpu_seconds=2, wall_seconds=2)
GEN = SearchAction("gen", "generate", ResourceVector(tokens=2))
REP = SearchAction("repair", "repair", ResourceVector(tokens=1))
TEST = SearchAction("test", "test", ResourceVector(test_calls=1))
STAT = SearchAction("static", "static_analysis", ResourceVector(cpu_seconds=1))


def session(keys=(A,), budget=CAP, attempted=(), observations=(), cap=8):
    archive = tuple(SearchCandidate(k, "initial") for k in keys)
    return SharedSession(
        CAP if budget == CAP else budget,
        SearchState(budget, archive, keys[0] if keys else None,
                    attempted, observations),
        max_candidates=cap,
    )


class MatchedOpportunityTests(unittest.TestCase):
    def test_generate_exactly_one_target_free(self):
        menu = matched_opportunities(session((A, B)), (GEN,))
        self.assertEqual(len(menu), 1)
        self.assertIsNone(menu[0].target)

    def test_diagnostics_target_all_candidates(self):
        menu = matched_opportunities(session((A, B)), (TEST, STAT))
        self.assertEqual({(o.action_id, o.target) for o in menu},
                         {("test", A), ("test", B),
                          ("static", A), ("static", B)})

    def test_repair_expands_over_all_candidates(self):
        menu = matched_opportunities(session((A, B)), (REP,))
        self.assertEqual([o.target for o in menu], [A, B])

    def test_no_diagnostic_without_candidate(self):
        self.assertEqual(matched_opportunities(session(()), (TEST, REP)), ())

    def test_candidate_cap_prevents_production(self):
        s = session((A, B), cap=2)
        self.assertEqual(matched_opportunities(s, (GEN, REP)), ())

    def test_one_use_action_id_blocks_every_target(self):
        s = session((A, B), attempted=("test",),
                    observations=(SearchObservation("test", A, "test", True),))
        self.assertEqual(matched_opportunities(s, (TEST,)), ())

    def test_budget_blocks_each_dimension(self):
        for field in RESOURCE_FIELDS:
            with self.subTest(field=field):
                a = SearchAction("g", "generate", ResourceVector(**{field: 2}))
                s = SharedSession.empty(ResourceVector(**{field: 1}))
                self.assertEqual(matched_opportunities(s, (a,)), ())

    def test_catalog_order_does_not_change_digest(self):
        s = session((A, B))
        self.assertEqual(opportunity_digest(s, (TEST, REP, GEN)),
                         opportunity_digest(s, (GEN, TEST, REP)))

    def test_archive_order_does_not_change_digest(self):
        self.assertEqual(opportunity_digest(session((A, B)), (TEST, REP)),
                         opportunity_digest(session((B, A)), (REP, TEST)))

    def test_digest_sensitive_to_action_cost_and_capacity(self):
        s = session((A,))
        self.assertNotEqual(
            opportunity_digest(s, (GEN,)),
            opportunity_digest(s, (SearchAction(
                "gen", "generate", ResourceVector(tokens=3)),)))
        self.assertNotEqual(opportunity_digest(s, (GEN,)),
                            opportunity_digest(session((A,), cap=1), (GEN,)))

    def test_digest_has_no_private_fields(self):
        self.assertFalse(any(
            x in Opportunity.__dataclass_fields__
            for x in ("prior", "posterior", "oracle", "likelihood", "correctness")
        ))
        self.assertEqual(len(opportunity_digest(session(), (TEST,))), 64)

    def test_baseline_can_target_non_active_patch(self):
        old = SearchAction("old", "test", ResourceVector(test_calls=1))
        s = commit_shared(
            session((A, B)), (old, REP),
            SharedDecision("old", "test", B, old.cost),
            reported_cost=old.cost, observed_positive=False)
        s = replace(s, state=replace(s.state, active_sha256=A))
        decision = choose_matched_baseline(
            s, (REP, old), SearchPolicy(depth=1))
        self.assertEqual((decision.action_id, decision.target_sha256),
                         ("repair", B))

    def test_baseline_uses_no_posterior_input(self):
        self.assertEqual(set(choose_matched_baseline.__code__.co_varnames[:3]),
                         {"session", "actions", "policy"})

    def test_baseline_target_free_generate(self):
        d = choose_matched_baseline(
            SharedSession.empty(CAP), (GEN,), SearchPolicy(depth=1))
        self.assertEqual((d.kind, d.target_sha256), ("generate", None))

    def test_record_rejects_forged_target(self):
        s = SharedSession.empty(CAP)
        p = SearchPolicy(depth=1)
        d = choose_matched_baseline(s, (GEN,), p)
        with self.assertRaisesRegex(ValueError, "unselected"):
            record_matched_baseline(
                s, (GEN,), p, replace(d, target_sha256=A),
                reported_cost=GEN.cost, new_candidate_sha256=A)

    def test_symbolic_target_cannot_be_committed(self):
        with self.assertRaisesRegex(ValueError, "symbolic target"):
            Opportunity("repair", "repair", ("future", "gen"),
                        REP.cost).as_decision()

    def test_matched_baseline_can_record_real_sha(self):
        s = SharedSession.empty(CAP)
        p = SearchPolicy(depth=1)
        d = choose_matched_baseline(s, (GEN,), p)
        nxt = record_matched_baseline(
            s, (GEN,), p, d, reported_cost=GEN.cost, new_candidate_sha256=A)
        self.assertEqual(nxt.state.candidates[0].sha256, A)


if __name__ == "__main__":
    unittest.main()
