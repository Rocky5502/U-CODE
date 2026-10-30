"""Adversarial offline tests for public-history/belief replay integrity.

These are hypothetical models; they do not verify any real patch, tool
receipt, independently sealed oracle, or resource meter.
"""
from dataclasses import replace
import unittest

from ucode.coherent_history_replay import (
    plan_verified_coherent_evidence, replay_coherent_history,
)
from ucode.coherent_hypothesis_search import (
    EvidenceHypothesis, initial_coherent_state,
    plan_coherent_evidence, record_coherent_observation,
)
from ucode.conditional_bes import (
    ConditionalKernel, ConditionalProbe, ConditionalRow, Observation,
)
from ucode.vector_policy import ResourcePrices, ResourceVector
from ucode.voi import ReleaseRule


CAL = ConditionalProbe("cal", "retrieve", ResourceVector(tokens=1))
DIAG = ConditionalProbe("diag", "test", ResourceVector(test_calls=1))
PROBES = (CAL, DIAG)
PRICES = ResourcePrices(tokens=.01, test_calls=.01)
RULE = ReleaseRule(max_predicted_failure=.1)


def hypotheses():
    result = []
    for ident, calibration, diagnostic_sensitivity in (
        ("A", 1., 1.), ("B", 0., 0.),
    ):
        rows = []
        for action, good, bad, other in (
            ("cal", calibration, calibration, "diag"),
            ("diag", diagnostic_sensitivity, 1-diagnostic_sensitivity, "cal"),
        ):
            for history in ((), (Observation(other, True),),
                            (Observation(other, False),)):
                rows.append(ConditionalRow(action, history, good, bad))
        result.append(EvidenceHypothesis(ident, ConditionalKernel(tuple(rows))))
    return tuple(result)


class CoherentHistoryReplayTests(unittest.TestCase):
    def setUp(self):
        self.models = hypotheses()
        self.start = initial_coherent_state(
            .5, self.models, (.5, .5),
            ResourceVector(tokens=1, test_calls=1),
        )
        self.after_cal = record_coherent_observation(
            self.start, CAL, self.models, True,
        )
        self.after_both = record_coherent_observation(
            self.after_cal, DIAG, self.models, True,
        )

    def replay(self, claimed, *, initial=None, probes=PROBES, models=None):
        return replay_coherent_history(
            self.start if initial is None else initial,
            claimed, probes, self.models if models is None else models,
        )

    def test_zero_step_and_two_step_replay_reconstruct_exact_state(self):
        self.assertEqual(self.replay(self.start), self.start)
        self.assertEqual(self.replay(self.after_cal), self.after_cal)
        self.assertEqual(self.replay(self.after_both), self.after_both)

    def test_verified_wrapper_matches_direct_planner_on_genuine_history(self):
        verified = plan_verified_coherent_evidence(
            self.start, self.after_cal, PROBES, self.models,
            PRICES, RULE, horizon=2,
        )
        direct = plan_coherent_evidence(
            self.after_cal, PROBES, self.models, PRICES, RULE,
            horizon=2,
        )
        self.assertEqual(verified, direct)
        self.assertEqual(verified.action, "diag")

    def test_forged_acceptability_posterior_rejected(self):
        fake = replace(self.after_cal, joint=((0., 1.), (0., 0.)))
        # Direct planning may accept this authored hypothetical state,
        # but the integration guard must never claim it follows cal+.
        self.assertNotEqual(fake, self.after_cal)
        with self.assertRaisesRegex(ValueError, "posterior"):
            self.replay(fake)
        with self.assertRaisesRegex(ValueError, "posterior"):
            plan_verified_coherent_evidence(
                self.start, fake, PROBES, self.models, PRICES, RULE,
            )

    def test_counterfeit_resource_refund_rejected(self):
        fake = replace(
            self.after_cal,
            budget=ResourceVector(tokens=1, test_calls=1),
        )
        with self.assertRaisesRegex(ValueError, "resource"):
            self.replay(fake)

    def test_fake_history_with_no_matching_posterior_rejected(self):
        fake = replace(
            self.after_cal,
            history=(Observation("cal", False),),
        )
        with self.assertRaisesRegex(ValueError, "posterior"):
            self.replay(fake)

    def test_unknown_or_missing_action_catalog_rejected(self):
        with self.assertRaisesRegex(ValueError, "frozen catalog"):
            self.replay(self.after_both, probes=(CAL,))
        with self.assertRaisesRegex(ValueError, "duplicate frozen"):
            self.replay(self.after_cal, probes=(CAL, CAL))

    def test_model_replacement_after_observation_rejected(self):
        changed = list(self.models)
        changed[0] = EvidenceHypothesis(
            "A", ConditionalKernel((
                ConditionalRow("cal", (), .8, .8),
            )),
        )
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.replay(self.after_cal, models=tuple(changed))

    def test_different_frozen_start_cannot_validate_claim(self):
        another = initial_coherent_state(
            .7, self.models, (.5, .5),
            ResourceVector(tokens=1, test_calls=1),
        )
        with self.assertRaisesRegex(ValueError, "posterior"):
            self.replay(self.after_cal, initial=another)

    def test_start_must_have_no_observations(self):
        with self.assertRaisesRegex(ValueError, "precede every"):
            self.replay(self.after_both, initial=self.after_cal)

    def test_structural_replay_does_not_claim_external_attestation(self):
        planned = plan_verified_coherent_evidence(
            self.start, self.after_both, PROBES, self.models,
            PRICES, RULE,
        )
        self.assertEqual(planned.action, "release")
        self.assertEqual(planned.real_task_results, 0)
        self.assertIn("NOT_CALIBRATED", planned.interpretation)


if __name__ == "__main__":
    unittest.main()
