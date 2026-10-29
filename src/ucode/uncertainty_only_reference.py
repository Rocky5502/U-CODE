"""A bounded uncertainty-trigger-only control, offline SYNTHETIC reference.

This local reference is NOT calibrated, a published benchmark reproduction,
an independent correctness model, or a real agent. It applies a frozen
synthetic prior and one public test likelihood to a single active candidate,
without candidate-space search or repairing after rejection.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import re

from .action_id_replay_bridge import ActionBoundBook
from .matched_opportunities import matched_opportunities
from .matched_session import SharedDecision, SharedSession
from .vector_policy import ResourceVector

_SHA = re.compile(r"^[0-9a-f]{64}$")


def _prob(x: float) -> bool:
    return type(x) in (float, int) and isfinite(x) and 0 <= x <= 1


@dataclass(frozen=True)
class SyntheticConfidenceCard:
    """Offline assumed numbers only; never evaluator outcomes or gold labels."""
    candidate_sha256: str
    prior_acceptable: float
    test_sensitivity: float
    test_specificity: float

    def __post_init__(self):
        if type(self.candidate_sha256) is not str or not _SHA.fullmatch(self.candidate_sha256):
            raise ValueError("candidate fingerprint must be SHA256")
        if any(not _prob(getattr(self,key))
               for key in ("prior_acceptable","test_sensitivity","test_specificity")):
            raise ValueError("synthetic confidence probabilities must be finite [0,1]")


@dataclass(frozen=True)
class SyntheticRiskRegister:
    cards: tuple[SyntheticConfidenceCard, ...]
    release_min_probability: float = 0.9

    def __post_init__(self):
        if type(self.cards) is not tuple or not self.cards or any(
                not isinstance(x,SyntheticConfidenceCard) for x in self.cards):
            raise ValueError("nonempty immutable synthetic confidence cards required")
        if len(set(x.candidate_sha256 for x in self.cards)) != len(self.cards):
            raise ValueError("duplicate candidate confidence")
        if not _prob(self.release_min_probability) or not 0 < self.release_min_probability <= 1:
            raise ValueError("release threshold must be frozen in (0,1]")

    def card(self,sha: str) -> SyntheticConfidenceCard | None:
        return next((x for x in self.cards if x.candidate_sha256 == sha),None)


def _posterior(card: SyntheticConfidenceCard, positive: bool) -> float | None:
    if type(positive) is not bool:
        raise TypeError("only public binary diagnostic signs supported")
    p=card.prior_acceptable
    yes=(card.test_sensitivity if positive else 1-card.test_sensitivity)
    no=(1-card.test_specificity if positive else card.test_specificity)
    denominator=p*yes+(1-p)*no
    if denominator <= 0:
        return None
    return (p*yes)/denominator


def choose_uncertainty_only_reference(
    session: SharedSession,
    book: ActionBoundBook,
    register: SyntheticRiskRegister,
) -> SharedDecision:
    """Generate once; risk-gate release or buy ONE test, then terminate.

    Frozen card probabilities are deliberately HYPOTHETICAL. This method
    performs no optimization over code generation, patch alternatives,
    test cost/VOI, or multi-step evidence correlation.
    """
    if not isinstance(session, SharedSession) or not isinstance(book, ActionBoundBook):
        raise TypeError("typed offline shared session and book required")
    if not isinstance(register,SyntheticRiskRegister):
        raise TypeError("typed synthetic confidence register required")
    menu=matched_opportunities(session,book.catalog)
    zero=ResourceVector()
    if not session.state.candidates:
        if session.state.attempted:
            return SharedDecision("abstain","abstain",None,zero)
        generate=next((x for x in menu if x.kind=="generate"),None)
        return generate.as_decision() if generate else SharedDecision("abstain","abstain",None,zero)
    target=session.state.candidates[-1].sha256
    card=register.card(target)
    if card is None:
        return SharedDecision("abstain","abstain",None,zero)
    obs=tuple(x for x in session.state.observations
              if x.candidate_sha256==target and x.kind=="test")
    if len(obs)>1:
        raise ValueError("single-test uncertainty-only reference cannot pool dependent tests")
    if obs:
        posterior=_posterior(card,obs[0].positive)
        if posterior is not None and posterior>=register.release_min_probability:
            return SharedDecision("release","release",target,zero)
        return SharedDecision("abstain","abstain",None,zero)
    if card.prior_acceptable>=register.release_min_probability:
        return SharedDecision("release","release",target,zero)
    test=next((x for x in menu if x.kind=="test" and x.target==target),None)
    return test.as_decision() if test else SharedDecision("abstain","abstain",None,zero)
