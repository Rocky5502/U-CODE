"""Audit all 33 labeled Springer math equations without claiming proofs.

A source label is not a validated theorem. The seven selected high-risk
equations have limited *synthetic/exact-arithmetic* cross-checks; all other
labels remain pending independent derivation and external peer review.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/"paper/overleaf/main.tex"
LABEL=re.compile(r"\\label\{(eq:[a-zA-Z0-9_-]+)\}")

LIMITED_CROSSCHECKS={
    "eq:evsi": "exact one-step evidence value on finite synthetic probabilities",
    "eq:beszero": "exact terminal utility and risk-gate boundary examples",
    "eq:bes": "independent exhaustive two-diagnostic finite counterexample only",
    "eq:conditional-bayes": "exact binary Bayes posterior and martingale grid",
    "eq:risk": "conditional wrong-release risks enumerated across missing cells",
    "eq:itt_missing_envelope": "exact finite integer missingness enumeration",
    "eq:coverage_missing_envelope": "exact finite integer missingness enumeration",
}
EXPECTED_FROZEN_LABELS={
    "eq:state","eq:budget","eq:success","eq:risk","eq:objective",
    "eq:bellman","eq:evsi","eq:one_step_gain","eq:myopic",
    "eq:beszero","eq:bes","eq:conditional-likelihood",
    "eq:conditional-bayes","eq:robust-gain","eq:robust-bounds",
    "eq:robust-probe","eq:robust-mixed","eq:joint-scenario-generator",
    "eq:joint-scenario-allocation","eq:oracle-ambiguity",
    "eq:sensitivity","eq:specificity","eq:action-parity",
    "eq:blind-heuristic-beam","eq:joint-archive-state",
    "eq:archive-stop","eq:joint-archive-bellman",
    "eq:joint-truth-update","eq:paired","eq:receipt-integrity",
    "eq:attrition-bounds","eq:itt_missing_envelope",
    "eq:coverage_missing_envelope",
}

def audit_equations(tex: str) -> dict:
    if not isinstance(tex,str) or not tex.strip():
        raise ValueError("nonempty manuscript source required")
    # Ignore comment-only lines before counting equation IDs.
    uncommented="\n".join(
        re.sub(r"(?<!\\)%[^\n]*$","",line) for line in tex.splitlines())
    found=LABEL.findall(uncommented)
    if len(found)!=len(set(found)):
        raise ValueError("duplicate mathematical equation IDs")
    if set(found)!=EXPECTED_FROZEN_LABELS:
        raise ValueError("frozen manuscript equation register drift; manually review additions/deletions")
    if not set(LIMITED_CROSSCHECKS).issubset(found):
        raise AssertionError("crosschecked equation missing")
    rows=[]
    for idx,label in enumerate(found,1):
        cross=LIMITED_CROSSCHECKS.get(label)
        rows.append({
            "equation_id":label,
            "order":idx,
            "source_verified_present":True,
            "scope":cross if cross else "no independent mathematical cross-check in this audit",
            "stage":"LIMITED_SYNTHETIC_CROSSCHECK" if cross else "PENDING_DERIVATION_REVIEW",
            "external_human_reviewed":False,
            "empirically_validated":False,
            "statistical_guarantee_established":False,
        })
    return {
        "status":"SOURCE_REGISTER_WITH_LIMITED_OFFLINE_MATH_CHECKS",
        "total_equations":len(rows),
        "limited_synthetic_crosschecks":len(LIMITED_CROSSCHECKS),
        "pending_independent_derivation":len(rows)-len(LIMITED_CROSSCHECKS),
        "full_theorem_reviews_completed":0,
        "real_model_evaluations":0,
        "equations":rows,
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,
                        default=Path("dist/ucode-equation-audit.json"))
    args=parser.parse_args()
    out=audit_equations(PAPER.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k!="equations"},
                     sort_keys=True,indent=2))

if __name__=="__main__":
    main()
