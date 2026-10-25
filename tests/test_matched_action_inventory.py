"""Synthetic action parity: exact same tools/costs, no forecasts leaked."""
from dataclasses import replace
import unittest

from ucode.matched_action_inventory import audit_action_parity
from ucode.blind_search import BlindAction
from ucode.budgeted_belief_search import (
    EvidenceAction, CandidateAction, CandidateScenario,
)
from ucode.vector_policy import ResourceVector

BUDGET=ResourceVector(tokens=100,test_calls=3,cpu_seconds=3)


def match():
    forecast=(
        CandidateAction("gen","generate",
                        (CandidateScenario(1,.4),),
                        ResourceVector(tokens=20)),
        EvidenceAction("test","test",.8,.75,ResourceVector(test_calls=1)),
        CandidateAction("repair","repair",
                        (CandidateScenario(1,.6),),
                        ResourceVector(tokens=10)),
        EvidenceAction("static","static_analysis",.9,.9,
                       ResourceVector(cpu_seconds=1)),
    )
    blind=(
        BlindAction("gen","generate",ResourceVector(tokens=20),0),
        BlindAction("test","test",ResourceVector(test_calls=1),1),
        BlindAction("repair","repair",ResourceVector(tokens=10),2),
        BlindAction("static","static_analysis",ResourceVector(cpu_seconds=1),3),
    )
    return forecast,blind


class MatchedActionInventoryTests(unittest.TestCase):
    def verify(self, fore=None, blind=None, bes_budget=BUDGET,
               blind_budget=BUDGET):
        f,b=match()
        return audit_action_parity(f if fore is None else fore,
                                   b if blind is None else blind,
                                   bes_initial_budget=bes_budget,
                                   blind_initial_budget=blind_budget)

    def test_identical_action_budget_inventory_passes(self):
        z=self.verify()
        self.assertEqual(z.action_count,4)
        self.assertEqual(z.action_ids,("gen","repair","static","test"))
        self.assertEqual(len(z.action_opportunity_sha256),64)
        self.assertEqual(len(z.resource_components),5)

    def test_reordering_actions_does_not_change_fingerprint(self):
        f,b=match()
        self.assertEqual(self.verify().action_opportunity_sha256,
                         self.verify(f[::-1],b[::-1]).action_opportunity_sha256)

    def test_probabilities_never_enter_common_inventory_fingerprint(self):
        f,b=match()
        changed=(
            replace(f[0],scenarios=(CandidateScenario(1,.99),)),
            replace(f[1],sensitivity=.1,specificity=.3),
            replace(f[2],scenarios=(CandidateScenario(1,.01),)),
            replace(f[3],sensitivity=.01,specificity=.99),
        )
        self.assertEqual(self.verify().action_opportunity_sha256,
                         self.verify(changed,b).action_opportunity_sha256)

    def test_blind_action_priority_does_not_change_tool_parity(self):
        f,b=match()
        new=tuple(replace(a,priority=20-a.priority) for a in b)
        self.assertEqual(self.verify().action_opportunity_sha256,
                         self.verify(f,new).action_opportunity_sha256)

    def test_missing_baseline_action_cannot_pass(self):
        f,b=match()
        with self.assertRaisesRegex(ValueError,"action IDs"):
            self.verify(f,b[:-1])

    def test_extra_blind_tool_cannot_pass(self):
        f,b=match()
        extra=BlindAction("oracle-check","test",ResourceVector(test_calls=1),9)
        with self.assertRaisesRegex(ValueError,"action IDs"):
            self.verify(f,b+(extra,))

    def test_changed_kind_cannot_pass_even_same_action_id(self):
        f,b=match()
        altered=replace(b[1],kind="static_analysis")
        with self.assertRaisesRegex(ValueError,"action kind"):
            self.verify(f,(b[0],altered)+b[2:])

    def test_changed_one_resource_cost_cannot_pass(self):
        f,b=match()
        altered=replace(b[1],cost=ResourceVector(test_calls=2))
        with self.assertRaisesRegex(ValueError,"resource costs"):
            self.verify(f,(b[0],altered)+b[2:])

    def test_different_initial_budget_cannot_pass(self):
        with self.assertRaisesRegex(ValueError,"different hard vector"):
            self.verify(blind_budget=ResourceVector(tokens=101,test_calls=3,cpu_seconds=3))

    def test_duplicate_action_id_rejected(self):
        f,b=match()
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.verify(f+(f[0],),b)

    def test_opportunity_digest_changes_when_cap_changes(self):
        n=ResourceVector(tokens=100,test_calls=4,cpu_seconds=3)
        self.assertNotEqual(
            self.verify().action_opportunity_sha256,
            self.verify(bes_budget=n,blind_budget=n).action_opportunity_sha256)

    def test_blind_controller_is_not_equivalent_to_implemented_fitted_agent(self):
        self.assertIn("PREEXECUTION",self.verify().comparison_scope)
        self.assertIn("NOT_MATCHED_REAL_INFERENCE",self.verify().comparison_scope)

    def test_wrong_type_is_rejected_before_fingerprint(self):
        f,b=match()
        with self.assertRaisesRegex(ValueError,"typed"):
            self.verify(f,tuple(f))


if __name__=="__main__":
    unittest.main()
