"""SYNTHETIC matched-session and patch-conditional archive regression tests."""
from dataclasses import replace
import unittest

from ucode.budgeted_belief_search import CandidateAction, CandidateScenario
from ucode.conditional_bes import ConditionalKernel, ConditionalRow
from ucode.conditional_archive import (
    ConditionalArchiveInputs, plan_conditional_archive,
    record_conditional_archive,
)
from ucode.matched_session import (
    SharedDecision, SharedReceipt, SharedSession, baseline_shared_decision,
    commit_shared, record_baseline_shared, audit_shared_start,
)
from ucode.optimized_search import (
    SearchAction, SearchCandidate, SearchObservation, SearchPolicy, SearchState,
)
from ucode.vector_policy import RESOURCE_FIELDS, ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule

A, B = "a" * 64, "b" * 64
BUDGET = ResourceVector(tokens=20, test_calls=2,
                        gpu_seconds=2, cpu_seconds=3, wall_seconds=10)
GEN = SearchAction("gen", "generate", ResourceVector(tokens=2))
GEN2 = SearchAction("gen2", "generate", ResourceVector(tokens=2))
TEST = SearchAction("test", "test", ResourceVector(test_calls=1))
REPAIR = SearchAction("repair", "repair", ResourceVector(tokens=3))
STATIC = SearchAction("static", "static_analysis", ResourceVector(cpu_seconds=1))


def seeded(candidate=A):
    return SharedSession(
        BUDGET, SearchState(BUDGET, (SearchCandidate(candidate, "initial"),),
                            candidate))


def kernel(action="test", p_good=1.0, p_bad=0.0):
    return ConditionalKernel((ConditionalRow(action, (), p_good, p_bad),))


def conditional(priors=((A, 0.5),), kernels=None, forecasts=()):
    if kernels is None:
        kernels = ((A, kernel()),)
    return ConditionalArchiveInputs(
        priors=priors, kernels=kernels, generation=forecasts,
        prices=ResourcePrices(test_calls=0.01, tokens=.001),
        rule=ReleaseRule(max_predicted_failure=.1),
        max_candidates=8,
    )


class SharedArchiveTests(unittest.TestCase):
    def test_baseline_consumes_reported_not_nominal_five_cost(self):
        s = SharedSession.empty(BUDGET)
        p = SearchPolicy(depth=1)
        decision = baseline_shared_decision(s, (GEN,), p)
        self.assertEqual(decision.action_id, "gen")
        result = record_baseline_shared(s, (GEN,), p, decision,
                                        reported_cost=ResourceVector(tokens=4),
                                        new_candidate_sha256=A)
        self.assertEqual(result.state.remaining.tokens, 16)
        self.assertEqual(result.receipts[0].reserved_cost.tokens, 2)
        self.assertEqual(result.receipts[0].reported_cost.tokens, 4)
        self.assertEqual(result.state.candidates[0].created_by, "gen")
        self.assertEqual(result.reported_consumption.tokens, 4)

    def test_same_archive_and_tool_receipts_feed_both_policies(self):
        s = seeded()
        baseline = baseline_shared_decision(s, (TEST,), SearchPolicy(depth=1))
        posterior = plan_conditional_archive(s, (TEST,), conditional()).decision
        self.assertEqual((baseline.action_id, baseline.target_sha256),
                         (posterior.action_id, posterior.target_sha256))
        b = record_baseline_shared(
            s, (TEST,), SearchPolicy(depth=1), baseline,
            reported_cost=TEST.cost, observed_positive=True,
        )
        c = record_conditional_archive(
            s, (TEST,), conditional(), posterior,
            reported_cost=TEST.cost, observed_positive=True,
        )
        self.assertEqual(b.state, c.state)
        self.assertEqual(b.reported_consumption, c.reported_consumption)
        self.assertEqual(b.trace_sha256, c.trace_sha256)
        self.assertEqual(b.state.observations[0].candidate_sha256, A)
        self.assertEqual(plan_conditional_archive(c,(TEST,),conditional()).decision.kind,
                         "release")

    def test_conditional_bes_uses_actual_visible_posterior(self):
        s = seeded()
        inp = conditional()
        d = plan_conditional_archive(s,(TEST,),inp).decision
        self.assertEqual(d.action_id, "test")
        s = record_conditional_archive(s, (TEST,), inp, d,
                                       reported_cost=TEST.cost,
                                       observed_positive=False)
        self.assertEqual(plan_conditional_archive(s, (TEST,), inp).decision.kind,
                         "abstain")

    def test_missing_candidate_prior_and_unknown_kernel_fail_closed(self):
        s = seeded()
        with self.assertRaisesRegex(ValueError,"exactly match"):
            plan_conditional_archive(s,(TEST,),conditional(priors=()),)
        with self.assertRaisesRegex(ValueError,"unknown archived"):
            plan_conditional_archive(
                s,(TEST,),conditional(kernels=((B,kernel()),)),)

    def test_missing_conditional_kernel_for_feasible_diagnostic_fails(self):
        with self.assertRaisesRegex(ValueError,"missing frozen kernel"):
            plan_conditional_archive(seeded(),(TEST,),
                                     conditional(kernels=()))

    def test_no_forecast_generation_cannot_be_assumed_successful(self):
        self.assertEqual(plan_conditional_archive(
            SharedSession.empty(BUDGET),(GEN,),
            conditional(priors=(),kernels=())).decision.kind,"abstain")

    def test_generation_transition_uses_frozen_forecast_and_shared_archive(self):
        s = SharedSession.empty(BUDGET)
        gen = CandidateAction("gen", "generate",
                              (CandidateScenario(1.0,.95),),GEN.cost)
        inp = conditional(priors=(),kernels=(),forecasts=(gen,))
        dec = plan_conditional_archive(s,(GEN,),inp).decision
        self.assertEqual(dec.action_id, "gen")
        s = record_conditional_archive(s,(GEN,),inp,dec,
                                      reported_cost=ResourceVector(tokens=3),
                                      new_candidate_sha256=A)
        self.assertEqual(s.state.remaining.tokens,17)
        self.assertEqual(s.state.candidates[0].created_by, "gen")
        next_inputs = conditional(priors=((A,.95),),kernels=())
        self.assertEqual(plan_conditional_archive(s,(GEN,),next_inputs).decision.kind,
                         "release")

    def test_repair_forecast_adds_child_without_rewriting_parent(self):
        s=seeded()
        forecast=CandidateAction("repair","repair",
                                 (CandidateScenario(1,.99),),REPAIR.cost)
        inp=conditional(priors=((A,.1),),kernels=(),forecasts=(forecast,))
        d=plan_conditional_archive(s,(REPAIR,),inp).decision
        self.assertEqual((d.action_id,d.target_sha256),("repair",A))
        result=record_conditional_archive(
            s,(REPAIR,),inp,d,reported_cost=REPAIR.cost,new_candidate_sha256=B)
        self.assertEqual(len(result.state.candidates),2)
        self.assertEqual(result.state.candidates[-1].parent_sha256,A)
        self.assertEqual(result.state.candidates[0].sha256,A)

    def test_high_prior_existing_candidate_is_not_replaced_without_gain(self):
        s=seeded()
        f=CandidateAction("gen","generate",
                          (CandidateScenario(1,.2),),GEN.cost)
        inp=conditional(priors=((A,.99),),kernels=(),forecasts=(f,))
        self.assertEqual(plan_conditional_archive(s,(GEN,),inp).decision.kind,
                         "release")

    def test_decision_invariant_to_catalog_order(self):
        s=seeded()
        f=CandidateAction("gen","generate",
                          (CandidateScenario(1,.95),),GEN.cost)
        inp=conditional(priors=((A,.1),),kernels=(),forecasts=(f,))
        # Catalog permutation must not alter the same feasible candidate
        # generation/repair comparison. No diagnostic kernel is provided.
        x=plan_conditional_archive(s,(GEN,REPAIR),inp)
        y=plan_conditional_archive(s,(REPAIR,GEN),inp)
        self.assertEqual(x.decision,y.decision)

    def test_all_five_reported_cost_limits_refuse_overspend(self):
        for field in RESOURCE_FIELDS:
            with self.subTest(field=field):
                one=ResourceVector(**{field:1})
                a=SearchAction("g","generate",one)
                ses=SharedSession.empty(one)
                d=SharedDecision("g","generate",None,one)
                costly=ResourceVector(**{field:2})
                with self.assertRaisesRegex(ValueError,"reported consumption"):
                    commit_shared(ses,(a,),d,reported_cost=costly,
                                  new_candidate_sha256=A)

    def test_reservation_cannot_be_overridden_by_lucky_report(self):
        s=SharedSession.empty(ResourceVector(tokens=1))
        d=SharedDecision("gen","generate",None,GEN.cost)
        with self.assertRaisesRegex(ValueError,"reserved action"):
            commit_shared(s,(GEN,),d,reported_cost=ResourceVector(tokens=1),
                          new_candidate_sha256=A)

    def test_replayed_action_or_forged_decision_rejected(self):
        s=SharedSession.empty(BUDGET)
        p=SearchPolicy(depth=1)
        d=baseline_shared_decision(s,(GEN,),p)
        with self.assertRaisesRegex(ValueError,"unselected"):
            record_baseline_shared(s,(GEN,),p,replace(d,target_sha256=A),
                                   reported_cost=GEN.cost,new_candidate_sha256=A)
        s=record_baseline_shared(s,(GEN,),p,d,reported_cost=GEN.cost,
                                 new_candidate_sha256=A)
        with self.assertRaisesRegex(ValueError,"single-use"):
            commit_shared(s,(GEN,),d,reported_cost=GEN.cost,
                          new_candidate_sha256=B)

    def test_no_hidden_oracle_outcome_is_action_result(self):
        s=SharedSession.empty(BUDGET)
        d=SharedDecision("gen","generate",None,GEN.cost)
        with self.assertRaisesRegex(ValueError,"oracle"):
            commit_shared(s,(GEN,),d,reported_cost=GEN.cost,
                          observed_positive=True,new_candidate_sha256=A)
        d2=SharedDecision("test","test",A,TEST.cost)
        with self.assertRaisesRegex(ValueError,"visible boolean"):
            commit_shared(seeded(),(TEST,),d2,reported_cost=TEST.cost,
                          observed_positive=1)

    def test_receipt_tampering_breaks_five_vector_reconciliation(self):
        s=SharedSession.empty(BUDGET)
        d=SharedDecision("gen","generate",None,GEN.cost)
        s=commit_shared(s,(GEN,),d,reported_cost=GEN.cost,
                        new_candidate_sha256=A)
        with self.assertRaisesRegex(ValueError,"does not reconcile"):
            replace(s,receipts=(replace(s.receipts[0],
                                        reported_cost=ResourceVector(tokens=1)),))
        with self.assertRaisesRegex(ValueError,"chronology"):
            replace(s,receipts=())

    def test_receipt_hash_changes_with_reported_cost(self):
        s=SharedSession.empty(BUDGET)
        d=SharedDecision("gen","generate",None,GEN.cost)
        first=commit_shared(s,(GEN,),d,reported_cost=GEN.cost,
                            new_candidate_sha256=A)
        second=commit_shared(s,(GEN,),d,reported_cost=ResourceVector(tokens=3),
                             new_candidate_sha256=A)
        self.assertNotEqual(first.trace_sha256,second.trace_sha256)

    def test_archive_cap_shared_for_both_policy_paths(self):
        s=SharedSession.empty(BUDGET,max_candidates=1)
        with self.assertRaisesRegex(ValueError,"archive capacity"):
            commit_shared(
                SharedSession(
                    BUDGET,SearchState(BUDGET,(SearchCandidate(A,"initial"),),A),
                    (),1),
                (GEN,),SharedDecision("gen","generate",A,GEN.cost),
                reported_cost=GEN.cost,new_candidate_sha256=B)
        with self.assertRaisesRegex(ValueError,"archive cap"):
            baseline_shared_decision(s,(GEN,),SearchPolicy(max_candidates=8))
        with self.assertRaisesRegex(ValueError,"archive cap"):
            plan_conditional_archive(s,(GEN,),conditional(priors=(),kernels=()))

    def test_different_reported_budget_does_not_retroactively_change_evidence(self):
        s=seeded()
        dec=SharedDecision("test","test",A,TEST.cost)
        out=commit_shared(s,(TEST,),dec,reported_cost=ResourceVector(test_calls=1,
                                                                     wall_seconds=3),
                          observed_positive=True)
        self.assertEqual(out.state.observations[0].candidate_sha256,A)
        self.assertEqual(out.state.remaining.wall_seconds,7)
        self.assertEqual(out.state.remaining.test_calls,1)

    def test_empty_candidate_release_is_never_allowed(self):
        s=SharedSession.empty(BUDGET)
        x=plan_conditional_archive(s,(GEN,),conditional(priors=(),kernels=()))
        self.assertEqual((x.decision.kind,x.decision.target_sha256),
                         ("abstain",None))

    def test_duplicate_priors_and_forecasts_are_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate content-keyed"):
            conditional(priors=((A,.2),(A,.3)))
        f=CandidateAction("gen","generate",
                          (CandidateScenario(1,.95),),GEN.cost)
        with self.assertRaisesRegex(ValueError,"duplicate candidate forecast"):
            conditional(priors=(),kernels=(),forecasts=(f,f))

    def test_reported_cost_does_not_claim_attested_telemetry(self):
        s=SharedSession.empty(BUDGET)
        self.assertNotIn("actual_costs_measured",SharedSession.__dataclass_fields__)
        self.assertNotIn("oracle_passed",SharedReceipt.__dataclass_fields__)
        self.assertTrue(s.trace_sha256)


    def test_matching_start_checks_archive_tools_and_budget_before_action(self):
        x=SharedSession.empty(BUDGET)
        match=audit_shared_start(x,x,(TEST,GEN),(GEN,TEST))
        self.assertEqual(match.action_count,2)
        self.assertEqual(len(match.action_opportunity_sha256),64)
        self.assertIn("OFFLINE_START_ONLY",match.scope)
        self.assertEqual(
            match.action_opportunity_sha256,
            audit_shared_start(x,x,(GEN,TEST),(TEST,GEN)).action_opportunity_sha256)

    def test_initial_opportunity_mismatches_are_all_refused(self):
        x=SharedSession.empty(BUDGET)
        y=SharedSession.empty(BUDGET,max_candidates=1)
        with self.assertRaisesRegex(ValueError,"archive capacity"):
            audit_shared_start(x,y,(GEN,),(GEN,))
        z=SharedSession.empty(ResourceVector(tokens=21,test_calls=2,
                                            gpu_seconds=2,cpu_seconds=3,
                                            wall_seconds=10))
        with self.assertRaisesRegex(ValueError,"five-resource budgets"):
            audit_shared_start(x,z,(GEN,),(GEN,))
        with self.assertRaisesRegex(ValueError,"action IDs, kinds"):
            audit_shared_start(x,x,(GEN,),(GEN2,))
        with self.assertRaisesRegex(ValueError,"action IDs, kinds"):
            audit_shared_start(x,x,(GEN,),(SearchAction(
                "gen","generate",ResourceVector(tokens=3)),))
        with self.assertRaisesRegex(ValueError,"action IDs, kinds"):
            audit_shared_start(x,x,(GEN,),(SearchAction(
                "gen","repair",GEN.cost),))

    def test_initial_candidate_archive_mismatch_is_refused(self):
        with self.assertRaisesRegex(ValueError,"initial candidate archive"):
            audit_shared_start(seeded(A),seeded(B),(TEST,),(TEST,))

    def test_matching_start_cannot_be_backdated_after_search(self):
        s=SharedSession.empty(BUDGET)
        d=SharedDecision("gen","generate",None,GEN.cost)
        progressed=commit_shared(s,(GEN,),d,reported_cost=GEN.cost,
                                 new_candidate_sha256=A)
        with self.assertRaisesRegex(ValueError,"precede policy"):
            audit_shared_start(progressed,progressed,(GEN,),(GEN,))

    def test_positive_visible_test_does_not_force_conditional_release(self):
        # SYNTHETIC counterexample to a universal U-CODE superiority claim:
        # fixed train-only adverse diagnostic kernel gives low posterior even
        # when simple blind test-count gate would release the same SHA.
        session=commit_shared(
            seeded(A),(TEST,),SharedDecision("test","test",A,TEST.cost),
            reported_cost=TEST.cost,observed_positive=True)
        baseline=baseline_shared_decision(session,(TEST,),SearchPolicy(depth=1))
        model=ConditionalArchiveInputs(
            priors=((A,.2),),kernels=((A,kernel("test",.2,.8)),),
            rule=ReleaseRule(max_predicted_failure=.1),
        )
        conditional_choice=plan_conditional_archive(session,(TEST,),model).decision
        self.assertEqual((baseline.kind,baseline.target_sha256),("release",A))
        self.assertEqual(conditional_choice.kind,"abstain")

    def test_old_patch_evidence_cannot_transfer_to_fresh_generated_patch(self):
        s=commit_shared(
            seeded(),(TEST,GEN),SharedDecision("test","test",A,TEST.cost),
            reported_cost=TEST.cost,observed_positive=True)
        s=commit_shared(s,(TEST,GEN),SharedDecision("gen","generate",None,GEN.cost),
                        reported_cost=GEN.cost,new_candidate_sha256=B)
        self.assertEqual(s.state.active_sha256,B)
        self.assertEqual([o.candidate_sha256 for o in s.state.observations],[A])
        inp=conditional(priors=((A,.5),(B,.1)),kernels=((A,kernel()),))
        outcome=plan_conditional_archive(s,(TEST,GEN),inp).decision
        self.assertEqual((outcome.kind,outcome.target_sha256),("release",A))


    def test_zero_reported_cost_is_not_accepted_as_measured_run(self):
        s=SharedSession.empty(BUDGET)
        d=SharedDecision("gen","generate",None,GEN.cost)
        with self.assertRaisesRegex(ValueError,"nonzero reported"):
            commit_shared(s,(GEN,),d,reported_cost=ResourceVector(),
                          new_candidate_sha256=A)

    def test_phantom_patch_in_receipt_cannot_pass_archive_consistency(self):
        s=commit_shared(
            SharedSession.empty(BUDGET),(GEN,),
            SharedDecision("gen","generate",None,GEN.cost),
            reported_cost=GEN.cost,new_candidate_sha256=A)
        with self.assertRaisesRegex(ValueError,"missing generated candidate"):
            replace(s,receipts=(replace(s.receipts[0],resulting_sha256=B),))

    def test_direct_receipt_forbids_invalid_or_missing_candidate_bindings(self):
        with self.assertRaisesRegex(ValueError,"SHA256"):
            SharedReceipt("gen","generate",None,"invalid",None,
                          GEN.cost,GEN.cost)
        with self.assertRaisesRegex(ValueError,"target candidate"):
            SharedReceipt("test","test",None,None,True,
                          TEST.cost,TEST.cost)
        with self.assertRaisesRegex(ValueError,"target candidate"):
            SharedReceipt("repair","repair",None,A,None,
                          REPAIR.cost,REPAIR.cost)


if __name__=="__main__":
    unittest.main()
