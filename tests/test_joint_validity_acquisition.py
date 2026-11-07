"""Independent synthetic falsifiers for exact three-way DRPA validity coupling.

No external PHP/Go code, LLM, test oracle, security metric or real task result.
Fractions-based analytic intersection bounds deliberately do NOT use the
production LP solver or production exact-HV function.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import unittest

from ucode.acquisition import ParetoPoint
from ucode.dependence_robust_acquisition import (
    RobustParetoProposal, TwoPointOutcome,
    bound_candidate_hvi, choose_dependence_robust_action,
)
from ucode.joint_validity_acquisition import (
    bound_joint_validity_hvi, choose_joint_validity_action,
)
from ucode.vector_policy import ResourcePrices, ResourceVector


CAP = ResourceVector(
    tokens=100, test_calls=3, gpu_seconds=5,
    cpu_seconds=9, wall_seconds=12,
)
PRICES = ResourcePrices(
    tokens=.1, test_calls=.05, gpu_seconds=.01,
    cpu_seconds=.001, wall_seconds=.001,
)


def proposal(
    name="a", p=.7, q=.7, v=.7,
    rlow=0., rhigh=1., slow=0., shigh=1.,
    cost=ResourceVector(tokens=1), action="generate",
):
    return RobustParetoProposal(
        name, action,
        TwoPointOutcome(rlow, rhigh, p),
        TwoPointOutcome(slow, shigh, q),
        v, cost,
    )


def check_witness(masses, p, q, v):
    # Independent verify of all four exact equality constraints.
    atoms = tuple(product((0, 1), repeat=3))
    w = tuple(F(s) for s in masses)
    assert len(w) == 8 and all(x >= 0 for x in w)
    assert sum(w) == 1
    assert sum(w[i] for i, xyz in enumerate(atoms) if xyz[0]) == F(str(p))
    assert sum(w[i] for i, xyz in enumerate(atoms) if xyz[1]) == F(str(q))
    assert sum(w[i] for i, xyz in enumerate(atoms) if xyz[2]) == F(str(v))


class JointValidityAcquisitionTests(unittest.TestCase):
    def test_all_high_intersection_has_known_sharp_three_event_bounds(self):
        # For empty archive and R=S=0/1, only R=S=VALID=1 earns
        # positive HVI. Its sharp three-event intersection bounds
        # are max(0,p+q+v-2) and min(p,q,v).
        for a, b, c in product(range(5), repeat=3):
            with self.subTest(high_marginals=(a,b,c)):
                p, q, v = a/4, b/4, c/4
                bounds = bound_joint_validity_hvi(
                    (),proposal(p=p,q=q,v=v),PRICES)
                self.assertAlmostEqual(
                    bounds.gross_hvi_range[0],max(0,p+q+v-2),
                    places=11)
                self.assertAlmostEqual(
                    bounds.gross_hvi_range[1],min(p,q,v),places=11)
                self.assertAlmostEqual(
                    bounds.fully_independent_gross_hvi,p*q*v,
                    places=11)
                self.assertLessEqual(bounds.feasible_vertices,70)
                self.assertGreaterEqual(bounds.feasible_vertices,1)
                check_witness(bounds.min_coupling_weights,p,q,v)
                check_witness(bounds.max_coupling_weights,p,q,v)
                # The legacy validity-independent range is a subset
                # of the correct three-way ambiguity class.
                self.assertLessEqual(
                    bounds.gross_hvi_range[0],
                    bounds.legacy_independent_validity_range[0]+1e-11)
                self.assertGreaterEqual(
                    bounds.gross_hvi_range[1]+1e-11,
                    bounds.legacy_independent_validity_range[1])

    def test_two_event_reduction_when_other_objective_fixed(self):
        # If safety=1 always, only R and VALID matter. q has no effect.
        for p, v in product((0.,.2,.5,.8,1.),repeat=2):
            with self.subTest(p=p,v=v):
                x=proposal(p=p,q=1.,v=v,slow=1.,shigh=1.)
                b=bound_joint_validity_hvi((),x,PRICES)
                self.assertAlmostEqual(
                    b.gross_hvi_range[0],max(0.,p+v-1.),places=10)
                self.assertAlmostEqual(
                    b.gross_hvi_range[1],min(p,v),places=10)

    def test_validity_certain_recovers_original_exact_two_way_bounds(self):
        for p,q in product((0.,.2,.6,1.),repeat=2):
            x=proposal(p=p,q=q,v=1.,rlow=.15,rhigh=.8,
                       slow=.35,shigh=.95)
            archive=(ParetoPoint(.5,.65),ParetoPoint(.75,.3))
            a=bound_joint_validity_hvi(archive,x,PRICES)
            b=bound_candidate_hvi(archive,x,PRICES)
            for actual, expected in zip(a.gross_hvi_range,b.gross_hvi_range):
                self.assertAlmostEqual(actual,expected,places=11)

    def test_exact_three_way_changes_previous_validity_independence_decision(self):
        # HVI is only P(R=1,S=1,VALID=1), p=q=v=.7.
        # Old restriction forces valid independent: lower=.7*.4=.28
        # New unrestricted lower=max(0,2.1-2)=.1
        # 2-token cost at .1/token => .2, hence old acts, new STOPS.
        x=proposal(cost=ResourceVector(tokens=2))
        old=choose_dependence_robust_action(
            (), (x,), CAP, PRICES)
        new=choose_joint_validity_action(
            (), (x,), CAP, PRICES)
        self.assertEqual(old.action_id, "a")
        self.assertEqual(new.action, "stop")
        self.assertIsNone(new.action_id)
        score=bound_joint_validity_hvi((),x,PRICES)
        self.assertAlmostEqual(score.gross_hvi_range[0], .1, places=12)
        self.assertAlmostEqual(score.legacy_independent_validity_range[0],
                               .28,places=12)
        self.assertAlmostEqual(score.net_hvi_range[0],-.1,places=12)

    def test_perfect_candidate_beats_ambiguity_if_lower_exceeds_rival_upper(self):
        risky=proposal("risky",p=.3,q=.3,v=.3,
                       cost=ResourceVector(tokens=1))
        strong=proposal("strong",p=1,q=1,v=1,rlow=0,rhigh=.9,
                        slow=0,shigh=.9,
                        cost=ResourceVector(tokens=2),action="repair")
        result=choose_joint_validity_action((),(risky,strong),CAP,PRICES)
        self.assertEqual(result.action_id,"strong")
        self.assertEqual(result.action,"repair")
        self.assertTrue(result.model_conditional_winner_separated)
        self.assertEqual(result.remaining_after.tokens,98)

    def test_ties_and_permutation_deterministic(self):
        a,b=proposal("a",p=1,q=1,v=1),proposal("b",p=1,q=1,v=1)
        one=choose_joint_validity_action((),(b,a),CAP,PRICES)
        two=choose_joint_validity_action((),(a,b),CAP,PRICES)
        self.assertEqual(one,two)
        self.assertEqual(one.action_id,"a")
        self.assertFalse(one.model_conditional_winner_separated)
        with self.assertRaisesRegex(ValueError,"duplicate candidate"):
            choose_joint_validity_action((),(a,a),CAP,PRICES)

    def test_each_five_resource_cap_is_hard(self):
        for field in ("tokens","test_calls","gpu_seconds",
                      "cpu_seconds","wall_seconds"):
            bad=proposal(
                "over-"+field,
                cost=ResourceVector(**{field:getattr(CAP,field)+1}))
            out=choose_joint_validity_action((),(bad,),CAP,PRICES)
            with self.subTest(field=field):
                self.assertIsNone(out.action_id)
                self.assertEqual(out.remaining_after,CAP)

    def test_zero_validity_perfect_archive_and_empty_menu_stop(self):
        for rows,archive in (
            ((proposal(v=0),),()),
            ((proposal(v=1),),(ParetoPoint(1,1),)),
            ((),()),
        ):
            result=choose_joint_validity_action(archive,rows,CAP,PRICES)
            self.assertIsNone(result.action_id)
            self.assertEqual(result.action,"stop")
            self.assertIsNone(result.selected)

    def test_nonzero_reference_exact_decimal_area(self):
        # Fixed R=.8 S=.7 V=1 and reference .2,.3:
        # exact area (.8-.2)*(.7-.3) = .24.
        x=proposal(p=1,q=1,v=1,rlow=0,rhigh=.8,slow=0,shigh=.7)
        s=bound_joint_validity_hvi(
            (),x,PRICES,reference=ParetoPoint(.2,.3))
        self.assertAlmostEqual(s.gross_hvi_range[0],.24,places=12)
        self.assertAlmostEqual(s.gross_hvi_range[1],.24,places=12)

    def test_witness_min_and_max_are_attainable_and_recompute_objective(self):
        p,q,v=.7,.7,.7
        s=bound_joint_validity_hvi((),proposal(p=p,q=q,v=v),PRICES)
        for w, expected in zip(
            (s.min_coupling_weights,s.max_coupling_weights),
            s.gross_hvi_range,
        ):
            check_witness(w,p,q,v)
            # In this independent all-high toy, only atom 111 pays one.
            self.assertAlmostEqual(float(F(w[7])),expected,places=12)

    def test_invalid_proposal_and_prices_fail_closed(self):
        x=proposal()
        with self.assertRaises(TypeError):
            bound_joint_validity_hvi((),object(),PRICES)
        with self.assertRaises(TypeError):
            bound_joint_validity_hvi((),x,object())
        with self.assertRaises(TypeError):
            bound_joint_validity_hvi((object(),),x,PRICES)
        with self.assertRaises(ValueError):
            bound_joint_validity_hvi(
                (ParetoPoint(.1,.1),)*257,x,PRICES)
        with self.assertRaises(TypeError):
            choose_joint_validity_action((),(object(),),CAP,PRICES)
        with self.assertRaises(TypeError):
            choose_joint_validity_action((),(x,),object(),PRICES)
        with self.assertRaises(ValueError):
            choose_joint_validity_action((),(x,)*65,CAP,PRICES)

    def test_diagnostics_cannot_be_misclassified_as_pareto_acquisition(self):
        for kind in ("test","retrieve","static_analysis","abstain"):
            with self.subTest(kind=kind),self.assertRaisesRegex(
                    ValueError,"only generate or repair"):
                proposal(action=kind)

    def test_no_hidden_gold_and_no_empirical_claim(self):
        r=bound_joint_validity_hvi((),proposal(),PRICES)
        self.assertIn("SYNTHETIC",r.interpretation)
        self.assertNotIn("oracle",r.__dict__)
        self.assertEqual(len(r.min_coupling_weights),8)
        self.assertEqual(len(r.max_coupling_weights),8)
        with self.assertRaises(TypeError):
            bound_joint_validity_hvi(
                (),replace(proposal(),action_id="a"),PRICES,
                oracle_passed=True)
        self.assertIn(
            "NOT_REAL_TASK_RESULT",
            choose_joint_validity_action((),(),CAP,PRICES).interpretation)


if __name__=="__main__":
    unittest.main()
