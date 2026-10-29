"""Independent exact-rational falsifier for multi-candidate evidence search.

This enumerator does NOT import or call either U-CODE planner, posterior
helper or terminal-value helper when computing oracle expectations.
Its models and latent truth atoms are entirely authored synthetic inputs;
the truth atoms are a generative model, NOT real hidden labels.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import unittest

from ucode.conditional_bes import ConditionalKernel, ConditionalRow, Observation
from ucode.correlated_archive_bes import (
    CandidateProfile, FrozenCorrelatedInputs, TruthAtom, plan_correlated_archive,
)
from ucode.joint_conditional_bes import (
    CandidateBelief, FrozenJointInputs, plan_joint_archive,
)
from ucode.matched_session import SharedSession
from ucode.optimized_search import SearchAction, SearchCandidate, SearchState
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


A, B = "a"*64, "b"*64
BUDGET = ResourceVector(test_calls=1, cpu_seconds=1)
TOOLS = (
    SearchAction("a", "test", ResourceVector(test_calls=1)),
    SearchAction("b", "static_analysis", ResourceVector(cpu_seconds=1)),
)
RULE = ReleaseRule(max_predicted_failure=.1)
PRICE_A, PRICE_B = F(1, 100), F(1, 50)


def sample_session():
    archive = (SearchCandidate(A, "initial"), SearchCandidate(B, "initial"))
    return SharedSession(
        BUDGET, SearchState(BUDGET, archive, A), max_candidates=2,
    )


def kernel(s_a, sp_a, s_b, sp_b):
    """P(+ | Y, history); exact action-local conditional independence."""
    rows = []
    for aid, other, sens, spec in (
        ("a", "b", s_a, sp_a), ("b", "a", s_b, sp_b),
    ):
        for history in (
            (), (Observation(other, True),), (Observation(other, False),),
        ):
            rows.append(
                ConditionalRow(aid, history, float(sens), float(1-spec))
            )
    return ConditionalKernel(tuple(rows))


def independent_truth_prior(p_a, p_b):
    """Joint distribution for TWO independent latent candidate bits."""
    result = []
    for bits in product((False, True), repeat=2):
        pa = p_a if bits[0] else 1-p_a
        pb = p_b if bits[1] else 1-p_b
        mass = pa*pb
        if mass:
            result.append((bits, mass))
    return tuple(result)


def exact_oracle(atoms, parameters):
    """Brute-force 2-step Bellman solver using ONLY rational arithmetic.

    Each action can be used once globally; either candidate may be probed.
    Evidence channels depend on a candidate's truth bit, not on sibling
    truth or other diagnostics, conditional on the latent joint prior.
    Scalar prices and five-component hard caps are fixed for this
    hypothetical two-action example. Results are expected utility,
    NOT actual task correctness.
    """
    assert sum(mass for _, mass in atoms) == 1
    likelihoods = {
        "a": (parameters[0], 1-parameters[1]),
        "b": (parameters[2], 1-parameters[3]),
    }
    costs = {"a": PRICE_A, "b": PRICE_B}

    def stop_value(dist):
        beliefs = [
            sum(mass for bits, mass in dist if bits[i])
            for i in (0, 1)
        ]
        def utility(p):
            return 2*p-1 if 1-p <= F(1,10) and 2*p-1 > 0 else F(0)
        return max(F(0), *(utility(p) for p in beliefs))

    @lru_cache(None)
    def solve(dist, used, steps):
        stop = stop_value(dist)
        best, selected = stop, None
        if steps == 0:
            return best, selected
        for action_id in ("a", "b"):
            if action_id in used:
                continue
            for target in (0, 1):
                expected = F(0)
                for positive in (True, False):
                    weighted = []
                    for bits, mass in dist:
                        p_positive = likelihoods[action_id][0 if bits[target] else 1]
                        probability = p_positive if positive else 1-p_positive
                        if mass*probability:
                            weighted.append((bits, mass*probability))
                    chance = sum((x[1] for x in weighted), F(0))
                    if not chance:
                        continue
                    posterior = tuple((bits, mass/chance)
                                      for bits, mass in weighted)
                    expected += chance*solve(
                        posterior, used | frozenset((action_id,)), steps-1,
                    )[0]
                candidate = expected-costs[action_id]
                if candidate > best:
                    best, selected = candidate, (action_id, (A, B)[target])
        return best, selected
    return solve(atoms, frozenset(), 2)


class IndependentJointBellmanOracleTests(unittest.TestCase):
    def check(self, atoms, parameters, *, factorized):
        oracle_value, oracle_action = exact_oracle(atoms, parameters)
        k = kernel(*parameters)
        prices = ResourcePrices(
            test_calls=float(PRICE_A), cpu_seconds=float(PRICE_B))
        correlated = FrozenCorrelatedInputs(
            (CandidateProfile(A, "shared"), CandidateProfile(B, "shared")),
            tuple(TruthAtom(bits, float(mass)) for bits, mass in atoms),
            (("shared", k),), (), prices, RULE, horizon=2,
            max_states=30000, max_atoms=16,
        )
        corr_plan = plan_correlated_archive(sample_session(), TOOLS, correlated)
        self.assertAlmostEqual(
            corr_plan.expected_proxy_utility, float(oracle_value), places=11)
        self.assertEqual(
            (corr_plan.decision.action_id, corr_plan.decision.target_sha256)
            if oracle_action else (corr_plan.decision.kind, None),
            oracle_action if oracle_action else
            ("release" if corr_plan.stop_utility>0 else "abstain", None),
        )
        if factorized:
            prior_a = sum(mass for bits, mass in atoms if bits[0])
            prior_b = sum(mass for bits, mass in atoms if bits[1])
            independent = FrozenJointInputs(
                (CandidateBelief(A, float(prior_a), "shared"),
                 CandidateBelief(B, float(prior_b), "shared")),
                (("shared", k),), (), prices, RULE, horizon=2,
            )
            plan = plan_joint_archive(sample_session(), TOOLS, independent)
            self.assertAlmostEqual(
                plan.expected_proxy_utility, float(oracle_value), places=11)
            if oracle_action:
                self.assertEqual(
                    (plan.decision.action_id, plan.decision.target_sha256),
                    oracle_action)
            else:
                self.assertIn(plan.decision.kind, ("release", "abstain"))

    def test_all_independent_two_patch_profiles_vs_exact_fraction_oracle(self):
        count = 0
        strengths = (F(1,2), F(3,4), F(1))
        for pa, pb, s_a, s_b in product(
            (F(1,4), F(1,2), F(3,4), F(19,20)),
            (F(1,4), F(1,2), F(3,4), F(19,20)),
            strengths, strengths,
        ):
            with self.subTest(pa=pa, pb=pb, a=s_a, b=s_b):
                self.check(
                    independent_truth_prior(pa, pb),
                    (s_a, s_a, s_b, s_b),
                    factorized=True,
                )
            count += 1
        self.assertEqual(count, 144)

    def test_correlated_truth_prior_grid_against_exact_fraction_oracle(self):
        independent = independent_truth_prior(F(1,2), F(1,2))
        same = (((False, False), F(1,2)), ((True, True), F(1,2)))
        opposite = (((False, True), F(1,2)), ((True, False), F(1,2)))
        asymmetric = (
            ((False, False), F(1,2)),
            ((True, False), F(1,4)),
            ((True, True), F(1,4)),
        )
        count=0
        for atoms, s_a, s_b in product(
            (independent, same, opposite, asymmetric),
            (F(1,2), F(3,4), F(1)),
            (F(1,2), F(3,4), F(1)),
        ):
            with self.subTest(prior=atoms, a=s_a, b=s_b):
                self.check(
                    atoms, (s_a,s_a,s_b,s_b),factorized=False)
            count+=1
        self.assertEqual(count,36)

    def test_finite_evidence_kernel_with_zero_mass_branch(self):
        atoms = (((False, False),F(1)),)
        self.check(atoms,(F(1),F(1),F(1),F(1)),factorized=True)


if __name__ == "__main__":
    unittest.main()
