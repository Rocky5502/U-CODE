"""Independent Fraction-based falsifiers for bounded dependence-robust EHVI.

All rows are deliberately synthetic; 0 repository tasks or LLM runs.
This oracle computes 2D rectangle UNION area from grid cells, without using
the production hypervolume routine or its Bayesian/Frechet helper.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import unittest

from ucode.acquisition import ParetoPoint
from ucode.dependence_robust_acquisition import (
    TwoPointOutcome, RobustParetoProposal, bound_candidate_hvi,
    choose_dependence_robust_action, choose_independence_baseline,
)
from ucode.vector_policy import ResourcePrices, ResourceVector


def exact_union(points):
    if not points:
        return F(0)
    xx = sorted({F(0)} | {p[0] for p in points})
    yy = sorted({F(0)} | {p[1] for p in points})
    area = F(0)
    for x0, x1 in zip(xx[:-1], xx[1:]):
        for y0, y1 in zip(yy[:-1], yy[1:]):
            midx, midy = (x0+x1)/2, (y0+y1)/2
            if any(midx <= x and midy <= y for x, y in points):
                area += (x1-x0)*(y1-y0)
    return area


def exact_bounds(archive, r, s, p, q):
    gains = {}
    before = exact_union(archive)
    for a, b in product((0, 1), repeat=2):
        new = (r[a], s[b])
        gains[a,b] = exact_union(archive + [new]) - before
    low, high = max(F(0), p+q-1), min(p,q)
    def value(t):
        return ((1-p-q+t)*gains[0,0] + (q-t)*gains[0,1]
                + (p-t)*gains[1,0] + t*gains[1,1])
    return min(value(low),value(high)), max(value(low),value(high)), value(p*q)


CAP = ResourceVector(tokens=20, test_calls=2, gpu_seconds=10,
                     cpu_seconds=10, wall_seconds=30)
PRICES = ResourcePrices(tokens=.01, test_calls=.02,
                        gpu_seconds=.03, cpu_seconds=.001,
                        wall_seconds=.002)


def proposal(name="a", action="generate", p=.7, q=.7, rlow=.1, rhigh=1.,
             slow=.1, shigh=1., cost=ResourceVector(tokens=1),
             valid=1.):
    return RobustParetoProposal(
        name, action, TwoPointOutcome(rlow,rhigh,p),
        TwoPointOutcome(slow,shigh,q), valid, cost)


class DependenceRobustAcquisitionTests(unittest.TestCase):
    def test_exact_fraction_grid_crosschecks_multiple_marginals_and_archives(self):
        for archive in ([], [(F(1,2),F(1,2))],
                        [(F(1,2),F(4,5)),(F(4,5),F(1,2))]):
            translated = [ParetoPoint(float(x),float(y)) for x,y in archive]
            for p,q in product((F(0),F(1,4),F(1,2),F(3,4),F(1)),repeat=2):
                with self.subTest(archive=archive,p=p,q=q):
                    x = proposal(
                        p=float(p), q=float(q),
                        rlow=.2,rhigh=.8,slow=.25,shigh=1.,
                        cost=ResourceVector(tokens=2),
                    )
                    v = bound_candidate_hvi(translated,x,PRICES)
                    lo,hi,ind = exact_bounds(
                        archive,(F(1,5),F(4,5)),(F(1,4),F(1)),
                        p,q)
                    self.assertAlmostEqual(v.gross_hvi_range[0],float(lo),places=11)
                    self.assertAlmostEqual(v.gross_hvi_range[1],float(hi),places=11)
                    self.assertAlmostEqual(v.independent_gross_hvi,float(ind),places=11)
                    self.assertLessEqual(v.gross_hvi_range[0]-1e-12,
                                         v.independent_gross_hvi)
                    self.assertLessEqual(v.independent_gross_hvi,
                                         v.gross_hvi_range[1]+1e-12)

    def test_dependency_ambiguity_reverses_nominal_action_choice(self):
        risky = proposal("risky",p=.7,q=.7,cost=ResourceVector(tokens=1))
        stable = proposal("stable",p=1,q=1,
                          rlow=.1,rhigh=.5,slow=.1,shigh=.96,
                          cost=ResourceVector(tokens=2))
        self.assertEqual(
            choose_independence_baseline([], (risky,stable), CAP, PRICES),
            "risky")
        decision=choose_dependence_robust_action([], (risky,stable),CAP,PRICES)
        self.assertEqual(decision.action_id,"stable")
        self.assertEqual(decision.action,"generate")
        self.assertAlmostEqual(
            bound_candidate_hvi([],risky,PRICES).gross_hvi_range[0],.46)
        self.assertAlmostEqual(
            bound_candidate_hvi([],risky,PRICES).independent_gross_hvi,.5329)
        self.assertFalse(decision.ranking_stable_over_independent_ambiguity_sets)

    def test_stable_winner_certified_only_with_separation(self):
        uncertain=proposal("uncertain", p=.5, q=.5)
        strong=proposal("strong", p=1, q=1,
                        rlow=0, rhigh=.95, slow=0, shigh=.95)
        choice=choose_dependence_robust_action([],(uncertain,strong),CAP,PRICES)
        self.assertEqual(choice.action_id,"strong")
        self.assertTrue(choice.ranking_stable_over_independent_ambiguity_sets)

    def test_hard_five_resource_caps_hold_independently(self):
        base=proposal("base",cost=ResourceVector(tokens=1))
        for field in ("tokens","test_calls","gpu_seconds","cpu_seconds","wall_seconds"):
            amount=getattr(CAP,field)+1
            bad=replace(base,cost=ResourceVector(**{field:amount}),
                        action_id="over-"+field)
            out=choose_dependence_robust_action([],(bad,),CAP,PRICES)
            with self.subTest(resource=field):
                self.assertIsNone(out.action_id)
                self.assertEqual(out.remaining_after,CAP)

    def test_no_action_when_archive_already_perfect(self):
        q=proposal("cannot-improve")
        out=choose_dependence_robust_action(
            [ParetoPoint(1,1)],(q,),CAP,PRICES)
        self.assertEqual(out.action,"stop")
        self.assertIsNone(out.selected)

    def test_invalid_forecasts_rejected(self):
        for item in (
            (1.1,.9,.5), (-.1,.5,.5), (.1,float("nan"),.5),
        ):
            with self.subTest(item=item),self.assertRaises(ValueError):
                TwoPointOutcome(*item)
        with self.assertRaisesRegex(ValueError,"ordered"):
            TwoPointOutcome(.8,.2,.5)
        with self.assertRaisesRegex(ValueError,"only generate or repair"):
            proposal(action="test")
        with self.assertRaisesRegex(ValueError,"consume resources"):
            proposal(cost=ResourceVector())
        with self.assertRaisesRegex(ValueError,"probability_valid"):
            proposal(valid=1.5)
        with self.assertRaisesRegex(ValueError,"bounded unique"):
            proposal(name="  ")

    def test_candidate_order_and_tie_break_are_deterministic(self):
        a=proposal("a",p=1,q=1)
        b=proposal("b",p=1,q=1)
        x=choose_dependence_robust_action([], (b,a), CAP, PRICES)
        y=choose_dependence_robust_action([], (a,b), CAP, PRICES)
        self.assertEqual(x,y)
        self.assertEqual(x.action_id,"a")
        self.assertFalse(x.ranking_stable_over_independent_ambiguity_sets)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            choose_dependence_robust_action([], (a,a), CAP, PRICES)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            choose_independence_baseline([], (a,a), CAP, PRICES)

    def test_diagnostic_actions_must_not_create_pareto_points(self):
        for kind in ("test","retrieve","static_analysis","abstain"):
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                proposal(action=kind)

    def test_validity_independence_assumption_is_explicit_not_risk_certificate(self):
        row=proposal(valid=0)
        score=bound_candidate_hvi([],row,PRICES)
        self.assertEqual(score.gross_hvi_range,(0,0))
        self.assertLess(score.robust_net_range[0],0)
        result=choose_dependence_robust_action([], (row,), CAP, PRICES)
        self.assertIsNone(result.action_id)
        self.assertIn("SYNTHETIC",result.interpretation)

    def test_corresponding_budget_spend_and_no_hidden_oracle_field(self):
        row=proposal(cost=ResourceVector(tokens=2,gpu_seconds=1))
        decision=choose_dependence_robust_action([], (row,),CAP,PRICES)
        self.assertEqual(decision.remaining_after.tokens,18)
        self.assertEqual(decision.remaining_after.gpu_seconds,9)
        with self.assertRaises(TypeError):
            RobustParetoProposal(**{**row.__dict__,"gold_oracle_passed":True})

    def test_nonzero_reference_does_not_create_fake_area(self):
        row=proposal(p=.5,q=.5, rlow=.2,rhigh=.9,slow=.3,shigh=.8)
        result=bound_candidate_hvi(
            [ParetoPoint(.6,.6)],row,PRICES,reference=ParetoPoint(.3,.4))
        self.assertLessEqual(result.gross_hvi_range[0],
                             result.independent_gross_hvi+1e-12)
        self.assertLessEqual(result.independent_gross_hvi,
                             result.gross_hvi_range[1]+1e-12)


if __name__=="__main__":
    unittest.main()
