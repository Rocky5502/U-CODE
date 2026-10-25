"""SYNTHETIC fixed-schedule baseline checks; NOT empirical software accuracy."""
from dataclasses import replace
import unittest

from ucode.blind_search import (
    BlindAction, BlindPolicy, BlindState, BlindDecision,
    VisibleObservation, blind_catalog_from_public_manifest, choose_blind,
    record_blind,
)
from ucode.vector_policy import ResourceVector

A = "a"*64
B = "b"*64
C = "c"*64


def actions():
    return (
        BlindAction("gen-1","generate",ResourceVector(tokens=20),0),
        BlindAction("retrieve-1","retrieve",ResourceVector(tokens=5),1),
        BlindAction("test-1","test",ResourceVector(test_calls=1),2),
        BlindAction("repair-1","repair",ResourceVector(tokens=12),3),
        BlindAction("test-2","test",ResourceVector(test_calls=1),4),
    )


def initial():
    return BlindState(ResourceVector(tokens=50,test_calls=2))


class BlindMatchedSearchTests(unittest.TestCase):
    def test_action_sequence_generate_retrieve_test_release(self):
        ac = actions()
        s = initial()
        d = choose_blind(s,ac)
        self.assertEqual((d.action,d.kind),("gen-1","generate"))
        s=record_blind(s,ac,d,new_candidate_sha256=A)
        d=choose_blind(s,ac)
        self.assertEqual(d.action,"retrieve-1")
        s=record_blind(s,ac,d,observed_positive=True)
        self.assertEqual(choose_blind(s,ac).action,"test-1")
        s=record_blind(s,ac,choose_blind(s,ac),observed_positive=True)
        self.assertEqual(choose_blind(s,ac).action,"release")
        self.assertEqual(s.remaining.tokens,25)
        self.assertEqual(s.remaining.test_calls,1)
        self.assertEqual(len(s.observations),2)

    def test_negative_test_triggers_repair_then_test_not_gold_reuse(self):
        ac=actions()
        s=BlindState(ResourceVector(tokens=30,test_calls=2),A,
                     ("gen-1","retrieve-1"),
                     (VisibleObservation("retrieve-1",A,True),))
        s=record_blind(s,ac,choose_blind(s,ac),observed_positive=False)
        self.assertEqual(choose_blind(s,ac).action,"repair-1")
        s=record_blind(s,ac,choose_blind(s,ac),new_candidate_sha256=B)
        self.assertEqual(s.candidate_sha256,B)
        self.assertEqual(s.observations,())
        self.assertEqual(choose_blind(s,ac).action,"test-2")
        s=record_blind(s,ac,choose_blind(s,ac),observed_positive=True)
        self.assertEqual(choose_blind(s,ac).action,"release")

    def test_positively_signed_retrieval_not_correctness_proof(self):
        ac=actions()
        s=BlindState(ResourceVector(tokens=20,test_calls=1),A,("retrieve-1",),
                     (VisibleObservation("retrieve-1",A,True),))
        self.assertEqual(choose_blind(s,ac).action,"test-1")
        s=replace(s,remaining=ResourceVector())
        self.assertEqual(choose_blind(s,ac).action,"abstain")

    def test_negative_static_analysis_requests_repair(self):
        ac=(BlindAction("scan","static_analysis",
                        ResourceVector(cpu_seconds=2),0),
            BlindAction("patch","repair",ResourceVector(tokens=10),1))
        s=BlindState(ResourceVector(tokens=11,cpu_seconds=2),A)
        s=record_blind(s,ac,choose_blind(s,ac),observed_positive=False)
        self.assertEqual(choose_blind(s,ac).action,"patch")

    def test_negative_result_with_no_repair_abstains(self):
        ac=(BlindAction("test","test",ResourceVector(test_calls=1),0),)
        s=BlindState(ResourceVector(test_calls=1),A)
        s=record_blind(s,ac,choose_blind(s,ac),observed_positive=False)
        self.assertEqual(choose_blind(s,ac).action,"abstain")

    def test_positive_test_requirement_can_be_predeclared(self):
        ac=(BlindAction("first","test",ResourceVector(test_calls=1),0),
            BlindAction("second","test",ResourceVector(test_calls=1),1))
        pol=BlindPolicy(min_positive_tests=2)
        s=BlindState(ResourceVector(test_calls=2),A)
        s=record_blind(s,ac,choose_blind(s,ac,pol),observed_positive=True,policy=pol)
        self.assertEqual(choose_blind(s,ac,pol).action,"second")
        s=record_blind(s,ac,choose_blind(s,ac,pol),observed_positive=True,policy=pol)
        self.assertEqual(choose_blind(s,ac,pol).action,"release")

    def test_no_candidate_repair_or_test_cannot_act(self):
        ac=actions()[1:]
        self.assertEqual(choose_blind(initial(),ac).action,"abstain")

    def test_hard_vector_budget_each_dimension(self):
        ac=(BlindAction("g","generate",
                        ResourceVector(tokens=1,gpu_seconds=1),0),)
        s=BlindState(ResourceVector(tokens=100,gpu_seconds=0))
        self.assertEqual(choose_blind(s,ac).action,"abstain")

    def test_priority_is_fixed_and_input_order_independent(self):
        ac=actions()
        x=choose_blind(initial(),ac).action
        y=choose_blind(initial(),ac[::-1]).action
        self.assertEqual(x,y)

    def test_tied_priorities_use_public_action_id_tiebreak(self):
        ac=(BlindAction("z","generate",ResourceVector(tokens=2),0),
            BlindAction("a","generate",ResourceVector(tokens=2),0))
        self.assertEqual(choose_blind(initial(),ac).action,"a")

    def test_no_predictions_or_oracle_in_visible_state(self):
        self.assertFalse(any(k in BlindState.__dataclass_fields__ for k in
                             ("prior","posterior","oracle_passed","sensitivity",
                              "specificity","gold_patch")))
        self.assertFalse(any(k in BlindAction.__dataclass_fields__ for k in
                             ("prior","posterior","oracle_passed","sensitivity",
                              "specificity","expected_terminal_value_after")))

    def test_catalog_rejects_forecast_field_and_hidden_labels(self):
        a=actions()[0]
        entry={"action_id":a.action_id,"kind":a.kind,"priority":a.priority,
               "cost":a.cost.__dict__}
        self.assertEqual(blind_catalog_from_public_manifest([entry])[0],a)
        for extra in ("oracle_passed","predicted_success","sensitivity",
                      "gold_patch","future_correctness"):
            with self.subTest(extra=extra),self.assertRaisesRegex(ValueError,"oracle leak"):
                blind_catalog_from_public_manifest([{**entry,extra:True}])

    def test_catalog_requires_all_five_cost_components(self):
        entry={"action_id":"a","kind":"test","priority":0,
               "cost":{"tokens":1}}
        with self.assertRaisesRegex(ValueError,"five resource"):
            blind_catalog_from_public_manifest([entry])

    def test_reject_duplicate_action_ids(self):
        ac=actions()
        with self.assertRaisesRegex(ValueError,"duplicate"):
            choose_blind(initial(),ac+(ac[0],))

    def test_action_must_consume_a_real_resource(self):
        with self.assertRaisesRegex(ValueError,"nonzero"):
            BlindAction("free","retrieve",ResourceVector(),0)

    def test_bad_release_gate_configuration_rejected(self):
        for n in (0,-1,1.5,True):
            with self.subTest(n=n),self.assertRaisesRegex(ValueError,"positive"):
                BlindPolicy(n)

    def test_reject_wrong_action_or_changed_budget_decision(self):
        s=initial()
        d=choose_blind(s,actions())
        with self.assertRaisesRegex(ValueError,"unselected"):
            record_blind(s,actions(),replace(d,budget_after_first=s.remaining),
                         new_candidate_sha256=A)

    def test_cannot_record_a_terminal_decision(self):
        ac=actions()
        s=BlindState(ResourceVector(),A,("test-1",),
                     (VisibleObservation("test-1",A,True),))
        self.assertTrue(choose_blind(s,ac).terminal)
        with self.assertRaisesRegex(ValueError,"terminal"):
            record_blind(s,ac,choose_blind(s,ac))

    def test_generation_cannot_import_evaluator_gold_label(self):
        s=initial()
        with self.assertRaisesRegex(ValueError,"cannot carry hidden"):
            record_blind(s,actions(),choose_blind(s,actions()),
                         observed_positive=True,new_candidate_sha256=A)

    def test_diagnostic_cannot_forge_candidate_replacement(self):
        s=BlindState(ResourceVector(test_calls=2),A)
        ac=(BlindAction("test","test",ResourceVector(test_calls=1),0),)
        with self.assertRaisesRegex(ValueError,"visible boolean"):
            record_blind(s,ac,choose_blind(s,ac),
                         observed_positive=True,new_candidate_sha256=B)

    def test_diagnostic_boolean_must_not_be_truthy_integer(self):
        s=BlindState(ResourceVector(test_calls=1),A)
        ac=(BlindAction("test","test",ResourceVector(test_calls=1),0),)
        with self.assertRaisesRegex(ValueError,"visible boolean"):
            record_blind(s,ac,choose_blind(s,ac),observed_positive=1)

    def test_stale_observation_cannot_follow_new_candidate(self):
        with self.assertRaisesRegex(ValueError,"stale"):
            BlindState(ResourceVector(),B,("test",),
                       (VisibleObservation("test",A,True),))

    def test_repair_with_identical_patch_is_blocked(self):
        ac=(BlindAction("repair","repair",ResourceVector(tokens=1),0),)
        s=BlindState(ResourceVector(tokens=1),A,("test",),
                     (VisibleObservation("test",A,False),))
        with self.assertRaisesRegex(ValueError,"changed candidate"):
            record_blind(s,ac,choose_blind(s,ac),new_candidate_sha256=A)

    def test_action_id_not_repeated_after_candidate_replacement(self):
        ac=(BlindAction("gen","generate",ResourceVector(tokens=1),0),
            BlindAction("test","test",ResourceVector(test_calls=1),1),
            BlindAction("repair","repair",ResourceVector(tokens=1),2))
        s=BlindState(ResourceVector(tokens=2,test_calls=1))
        s=record_blind(s,ac,choose_blind(s,ac),new_candidate_sha256=A)
        s=record_blind(s,ac,choose_blind(s,ac),observed_positive=False)
        s=record_blind(s,ac,choose_blind(s,ac),new_candidate_sha256=B)
        self.assertEqual(s.attempted,("gen","test","repair"))
        self.assertEqual(choose_blind(s,ac).action,"abstain")

    def test_invalid_hash_or_negative_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,"SHA256"):
            BlindState(ResourceVector(),candidate_sha256="branch-main")
        with self.assertRaises(ValueError):
            BlindState(ResourceVector(tokens=-1))

    def test_no_external_code_invocation_or_probability_dependent_ties(self):
        ac=(BlindAction("g1","generate",ResourceVector(tokens=10),0),
            BlindAction("g2","generate",ResourceVector(tokens=2),1))
        self.assertEqual(choose_blind(initial(),ac).action,"g1")

    def test_extra_observation_has_to_reference_executed_action(self):
        with self.assertRaisesRegex(ValueError,"prior action"):
            BlindState(ResourceVector(),A,(),
                       (VisibleObservation("secret-test",A,True),))


if __name__=="__main__":
    unittest.main()
