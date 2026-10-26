"""Strict synthetic parity fixtures: no model invocation or task oracle."""
import unittest

from ucode.budgeted_belief_search import (
    CandidateAction, CandidateScenario, EvidenceAction,
)
from ucode.blind_search import BlindAction
from ucode.matched_action_inventory import (
    audit_action_parity, audit_optimized_action_parity,
)
from ucode.optimized_search import SearchAction
from ucode.vector_policy import ResourceVector

BASE = ResourceVector(tokens=100, test_calls=3, cpu_seconds=4,
                      gpu_seconds=10, wall_seconds=20)


def inventories():
    bes = (
        CandidateAction("generate", "generate",
                        (CandidateScenario(1.0, 0.5),),
                        ResourceVector(tokens=8, gpu_seconds=1)),
        EvidenceAction("test", "test", .8, .9,
                       ResourceVector(test_calls=1, wall_seconds=1)),
        CandidateAction("repair", "repair",
                        (CandidateScenario(1.0, .6),),
                        ResourceVector(tokens=4)),
        EvidenceAction("analyze", "static_analysis", .9, .9,
                       ResourceVector(cpu_seconds=2)),
    )
    optimized = tuple(SearchAction(a.action_id, a.kind, a.cost) for a in bes)
    fixed = tuple(BlindAction(a.action_id, a.kind, a.cost, i)
                  for i, a in enumerate(bes))
    return bes, optimized, fixed


class OptimizedInventoryTests(unittest.TestCase):
    def audit(self, bes=None, optimized=None, first=BASE, second=BASE):
        b, o, _ = inventories()
        return audit_optimized_action_parity(
            b if bes is None else bes, o if optimized is None else optimized,
            bes_initial_budget=first, optimized_initial_budget=second)

    def test_shared_digest_matches_existing_blind_inventory(self):
        b, o, fixed = inventories()
        d = self.audit().action_opportunity_sha256
        self.assertEqual(d, audit_action_parity(
            b, fixed, bes_initial_budget=BASE,
            blind_initial_budget=BASE).action_opportunity_sha256)
        self.assertIn("ARCHIVE_AND_REAL_INFERENCE_NOT_MATCHED",
                      self.audit().comparison_scope)

    def test_order_and_prediction_changes_do_not_change_digest(self):
        b, o, _ = inventories()
        d = self.audit().action_opportunity_sha256
        new = (
            CandidateAction("generate", "generate",
                            (CandidateScenario(1.0, .99),),
                            b[0].cost),
            EvidenceAction("test", "test", .01, .3, b[1].cost),
            b[2], b[3],
        )
        self.assertEqual(d, self.audit(new[::-1], o[::-1]).action_opportunity_sha256)

    def test_missing_extra_or_duplicate_action_fails(self):
        b, o, _ = inventories()
        with self.assertRaises(ValueError):
            self.audit(b, o[1:])
        with self.assertRaises(ValueError):
            self.audit(b, o + (o[0],))
        with self.assertRaises(ValueError):
            self.audit(b, o + (SearchAction(
                "oracle", "test", ResourceVector(test_calls=1)),))

    def test_one_dimension_cost_budget_or_kind_mismatch_fails(self):
        b, o, _ = inventories()
        for cost in (ResourceVector(tokens=9, gpu_seconds=1),
                     ResourceVector(tokens=8, gpu_seconds=2)):
            altered = (SearchAction("generate", "generate", cost),) + o[1:]
            with self.assertRaisesRegex(ValueError, "resource costs"):
                self.audit(b, altered)
        altered = (SearchAction("generate", "repair", o[0].cost),) + o[1:]
        with self.assertRaisesRegex(ValueError, "kind"):
            self.audit(b, altered)
        with self.assertRaisesRegex(ValueError, "different hard"):
            self.audit(b, o, second=ResourceVector(
                tokens=100, test_calls=3, cpu_seconds=4,
                gpu_seconds=10, wall_seconds=19))

    def test_wrong_type_is_not_recast_as_optimized_control(self):
        b, o, fixed = inventories()
        with self.assertRaisesRegex(ValueError, "typed"):
            self.audit(b, fixed)


if __name__ == "__main__":
    unittest.main()
