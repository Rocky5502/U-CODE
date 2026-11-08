"""Conditional feasibility witnesses for Go #43's *pre-fix* specification.

Public, source-pinned questions for an independent domain reviewer. This file
does not implement settlement behavior, test a Go binary, choose a rounding
rule, authorize a task, or contain any golden/oracle answer.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Mapping

_GO_BASE = "ec41b1b33f5a4d46a8398fb6ccc33f25336fdb8a"
_DESIGN_BLOB = "b566ca7627b6518670a866a6a637bd5257e947f4"
_RULES_BLOB = "e71288e3127cb66f2471a5ddd2800092db0552cc"

# Conservative *review dependencies*, NOT a purported interpretation of rules.
# All cases depend on independently deciding whether the older rules are
# normatively applicable. This is not a claim that every case is inconsistent.
_AMBIGUITY_TO_CASES = {
    "ZERO_FLOOR_VS_TOTAL_CONSERVATION": (
        "LOW_BALANCE_SETTLEMENT",
        "TEAM_DISTRIBUTION_AND_CONSERVATION",
        "RANK_BOUNDARY_CROSSING",
    ),
    "HALL_COEFFICIENT_FRACTIONAL_ROUNDING": (
        "HALL_MULTIPLIER_CASES",
        "FRACTIONAL_HALL_MULTIPLIER",
        "RANK_BOUNDARY_CROSSING",
    ),
    "TEAM_PLAYER_SPLIT_AND_NONNEGATIVE_BALANCE": (
        "LOW_BALANCE_SETTLEMENT",
        "TEAM_DISTRIBUTION_AND_CONSERVATION",
        "RANK_BOUNDARY_CROSSING",
    ),
    "SPRING_RULE_SOURCE_AND_SCOPE": (
        "A_TWO_SINGLE_VS_SPRING",
        "HALL_MULTIPLIER_CASES",
    ),
    "ATOMIC_RETRY_IDENTITY_AND_OBSERVABILITY": (
        "ATOMIC_ALL_PLAYER_LEDGER",
        "RETRY_IDEMPOTENCE",
        "RECOVERY_AFTER_RECONNECT",
    ),
    "EXTERNAL_BUSINESS_RULES_PRECEDENCE": (
        "GAP_TIER_EDGES",
        "A_TWO_SINGLE_VS_SPRING",
        "HALL_MULTIPLIER_CASES",
        "LOW_BALANCE_SETTLEMENT",
        "FRACTIONAL_HALL_MULTIPLIER",
        "TEAM_DISTRIBUTION_AND_CONSERVATION",
        "RANK_BOUNDARY_CROSSING",
        "SETTLE_ONLY_ON_MATCH_COMPLETION",
        "NATURAL_LEVEL_NO_DIRECT_POINT_CHANGE",
        "ATOMIC_ALL_PLAYER_LEDGER",
        "RETRY_IDEMPOTENCE",
        "RECOVERY_AFTER_RECONNECT",
    ),
}

def _rational(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else (
        f"{value.numerator}/{value.denominator}"
    )

def conditional_capped_transfer_witness(
    *, credited_winners: int = 2,
    nominal_points_per_player: int = 5,
    losing_balances: tuple[int, ...] = (2, 2),
) -> dict:
    """Show a non-conservation witness only under explicitly assumed semantics.

    Assumptions: a fixed nominal credit per winning player; losing players
    have the same nominal debit but are capped at current nonnegative balance;
    no other wallet, transfer, subsidy, debt, or compensation is involved.
    The source does *not* establish that this is the intended implementation.
    """
    if (type(credited_winners) is not int or credited_winners <= 0
            or type(nominal_points_per_player) is not int
            or nominal_points_per_player <= 0
            or type(losing_balances) is not tuple
            or len(losing_balances) != credited_winners
            or any(type(x) is not int or x < 0 for x in losing_balances)):
        raise ValueError("positive equal-sized sides and nonnegative integer toy balances required")
    total_credit = credited_winners * nominal_points_per_player
    total_debit = sum(min(balance, nominal_points_per_player) for balance in losing_balances)
    residual = total_credit - total_debit
    return {
        "kind": "CONDITIONAL_TOY_INFEASIBILITY_NOT_GAME_ORACLE",
        "source_section": "design.md §3.2",
        "hypothesis": "fixed_per_winner_nominal_credit_and_capped_per_loser_debit_no_other_transfers",
        "credited_winner_count": credited_winners,
        "nominal_points_each": nominal_points_per_player,
        "hypothetical_loser_starting_balances": list(losing_balances),
        "hypothetical_total_credit": total_credit,
        "hypothetical_total_capped_debit": total_debit,
        "hypothetical_net_points_created": residual,
        "conserves_sum_under_assumptions": residual == 0,
        "independent_business_rule_selected": False,
        "oracle_result_or_expected_answer": False,
    }

def fractional_hall_witness(
    *, base_points: int = 5,
    multiplier_numerator: int = 3,
    multiplier_denominator: int = 2,
) -> dict:
    """Exact rational counterexample to an *implicit integer* settlement.

    No rounding or precision choice is proposed. 1.5 is documented as a hall
    multiplier; the illustrative five-point base is a source-era tier amount.
    """
    if (type(base_points) is not int or base_points <= 0
            or type(multiplier_numerator) is not int
            or multiplier_numerator <= 0
            or type(multiplier_denominator) is not int
            or multiplier_denominator <= 0):
        raise ValueError("positive integer multiplier and base required")
    fractional = Fraction(base_points) * Fraction(
        multiplier_numerator, multiplier_denominator)
    return {
        "kind": "EXACT_RATIONAL_TOY_CASE_NOT_ROUNDING_POLICY",
        "source_section": "design.md §3.2",
        "hypothetical_base_points": base_points,
        "documented_multiplier_as_fraction": _rational(
            Fraction(multiplier_numerator, multiplier_denominator)),
        "unrounded_nominal_points_exact": _rational(fractional),
        "requires_noninteger_representation_or_a_rule": fractional.denominator > 1,
        "integer_rounding_rule_selected": False,
        "oracle_result_or_expected_answer": False,
    }

def build_go43_spec_feasibility_packet(
    blueprint: Mapping, verified_handoff: Mapping,
) -> dict:
    """Build a public-only question dependency packet from verified metadata.

    The canonical original verifier must run first, not a caller-supplied
    attestation. We independently fail closed on promotion fields here.
    """
    if type(blueprint) is not dict or type(verified_handoff) is not dict:
        raise ValueError("canonical source-pinned blueprint and verifier report required")
    if (blueprint.get("stage") != "GO43_PUBLIC_REVIEW_QUESTIONS_NOT_EXECUTABLE_ORACLE"
            or blueprint.get("candidate_id") != 43
            or blueprint.get("task_scope") != "declared_microtask"
            or blueprint.get("base_commit") != _GO_BASE
            or blueprint.get("source_document_git_blob_sha40") != _DESIGN_BLOB
            or blueprint.get("business_rules_git_blob_sha40") != _RULES_BLOB
            or blueprint.get("external_business_rules_normativity_review") != "PENDING"
            or verified_handoff.get("stage") != "SOURCE_PINNED_REVIEW_HANDOFF_NOT_EXECUTABLE"
            or verified_handoff.get("candidate_id") != 43
            or verified_handoff.get("immutable_pre_fix_spec_blob_sha40") != _DESIGN_BLOB
            or verified_handoff.get("higher_priority_rules_git_blob_sha40") != _RULES_BLOB
            or verified_handoff.get("public_review_case_families") != 12
            or verified_handoff.get("unresolved_normative_ambiguities") != 6
            or verified_handoff.get("qualified_executable_tasks") != 0
            or verified_handoff.get("independently_approved_task_specification") is not False
            or verified_handoff.get("policy_prompt_authorized") is not False):
        raise ValueError("unverified Go source, hierarchy, task scope or approval")
    for k in ("independent_source_era_scope_approved", "source_file_rights_adjudicated",
              "oracle_independently_authored", "oracle_sealed_outside_repository",
              "sandbox_attested", "execution_metering_attested", "task_admitted",
              "go_executed"):
        if blueprint.get(k) is not False:
            raise ValueError("public Go blueprint cannot grant task admission: " + k)
    cases = blueprint.get("oracle_case_families")
    ambiguities = blueprint.get("ambiguity_register")
    if (type(cases) is not list or len(cases) != 12 or
            type(ambiguities) is not list or len(ambiguities) != 6):
        raise ValueError("canonical twelve-case/six-ambiguity set required")
    case_names = []
    for row in cases:
        if (type(row) is not dict or
                set(row) != {"case_id", "spec_sections", "stage", "gold_output_included"}
                or row.get("stage") != "PROPOSED_REVIEW_ONLY_NO_TEST_CODE_OR_GOLD"
                or row.get("gold_output_included") is not False):
            raise ValueError("prospective case drift or oracle gold leakage")
        case_names.append(row["case_id"])
    if len(set(case_names)) != 12 or set(case_names) != set(_AMBIGUITY_TO_CASES["EXTERNAL_BUSINESS_RULES_PRECEDENCE"]):
        raise ValueError("missing, duplicate or unexpected canonical Go case family")
    ambiguity_ids = []
    for row in ambiguities:
        if (type(row) is not dict or set(row) != {"ambiguity_id", "spec_section", "status"}
                or row.get("status") != "NEEDS_INDEPENDENT_SPEC_AUTHOR_RESOLUTION"):
            raise ValueError("source-era ambiguity cannot be self-resolved")
        ambiguity_ids.append(row["ambiguity_id"])
    if len(set(ambiguity_ids)) != 6 or set(ambiguity_ids) != set(_AMBIGUITY_TO_CASES):
        raise ValueError("missing, duplicate or unexpected canonical ambiguity")
    for deps in _AMBIGUITY_TO_CASES.values():
        if not set(deps) <= set(case_names):
            raise ValueError("review dependency refers to unknown case")
    dependencies = [
        {"ambiguity_id":row["ambiguity_id"],
         "original_section":row["spec_section"],
         "status":"AWAITING_INDEPENDENT_DOMAIN_DECISION",
         "affected_prospective_case_families":list(_AMBIGUITY_TO_CASES[row["ambiguity_id"]])}
        for row in ambiguities
    ]
    return {
        "schema_version":"1.0",
        "stage":"GO43_SPEC_CONSISTENCY_REVIEW_ONLY_NOT_EXECUTABLE",
        "candidate_id":43,
        "task_scope":"declared_microtask_not_full_PR",
        "pinned_base_commit":_GO_BASE,
        "pinned_original_documents":[
            {"path":"docs/design.md","git_blob_sha40":_DESIGN_BLOB},
            {"path":"docs/淮安80分业务规则.md","git_blob_sha40":_RULES_BLOB},
        ],
        "hypothetical_conditional_point_conservation_witness":conditional_capped_transfer_witness(),
        "hypothetical_exact_fraction_witness":fractional_hall_witness(),
        "independent_decision_dependencies":dependencies,
        "all_twelve_prospective_cases_require_normativity_review":True,
        "all_six_spec_questions_open":True,
        "independent_human_spec_resolution_received":False,
        "case_expected_outputs_included":False,
        "oracle_sealed":False,
        "task_admitted":False,
        "external_code_executed":False,
        "real_go_model_outcomes":0,
        "external_execution_authorized":False,
    }
