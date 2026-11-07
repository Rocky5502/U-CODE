"""Build a public, independent-reviewer Go #43 handoff (never run Go).

The source-era artifact `docs/design.md` must be supplied by a separate
trusted reviewer using the exact old repository base. This script does not
fetch or copy it; it can optionally verify its raw Git blob SHA-1 and report
an additional SHA-256 receipt without outputting document contents.

No post-PR solution code, gold, test patch, private user content or source
rights are inferred. Public review questions are not an executable oracle.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from ucode.go43_oracle_review_blueprint import (
    inspect_go43_local_pref_fix_document, inspect_go43_local_business_rules,
    verify_go43_oracle_review_blueprint,
)
from ucode.pilot_preflight import build_pilot_preflight,ROOT

_ADMISSION=ROOT/"data/admission"
_SOURCE=_ADMISSION/"2026-10-30/go43_immutable_pre_fix_spec_blob_METADATA_NOT_APPROVED.json"
_PLAN=_ADMISSION/"2026-11-07/go43_pre_fix_oracle_review_blueprint_PUBLIC_NO_GOLD.json"
_TREES=_ADMISSION/"2026-10-27/two_candidate_pre_fix_tree_inventory.json"
_ISSUES=_ADMISSION/"2026-10-27/two_candidate_issue_chronology_metadata.json"


def _read_json(p:Path)->dict:
    result=json.loads(p.read_text(encoding="utf-8"))
    if type(result) is not dict:
        raise ValueError("only canonical JSON object allowed")
    return result


def compile_go43_public_handoff(
    root:Path=ROOT,source_file:Path|None=None,
    business_rules_file:Path|None=None,
)->dict:
    root=Path(root)
    admission=root/"data/admission"
    plan=_read_json(admission/"2026-11-07/go43_pre_fix_oracle_review_blueprint_PUBLIC_NO_GOLD.json")
    verified=verify_go43_oracle_review_blueprint(
        plan,
        _read_json(admission/"2026-10-30/go43_immutable_pre_fix_spec_blob_METADATA_NOT_APPROVED.json"),
        build_pilot_preflight(root),
        _read_json(admission/"2026-10-27/two_candidate_pre_fix_tree_inventory.json"),
        _read_json(admission/"2026-10-27/two_candidate_issue_chronology_metadata.json"),
        _read_json(admission/"2026-11-07/go43_pre_fix_business_rules_blob_METADATA_NOT_APPROVED.json"),
    )
    summary={
        "schema_version":"1.0",
        **verified,
        "source_file_optional_external_witness":None,
        "business_rules_optional_external_witness":None,
        "case_categories_only_no_golds":[x["case_id"] for x in plan["oracle_case_families"]],
        "normative_questions_still_open":[x["ambiguity_id"] for x in plan["ambiguity_register"]],
        "all_original_go_admission_gates_pending":True,
        "external_reviewer_attestation_collected":False,
        "policy_input_from_post_pr_text_prohibited":True,
    }
    if (source_file is None)!=(business_rules_file is None):
        raise ValueError("both pre-fix design and higher-priority business rules must be supplied together")
    if source_file is not None:
        paths=(Path(source_file),Path(business_rules_file))
        if paths[0].resolve()==paths[1].resolve():
            raise ValueError("independent distinct local spec documents required")
        for path in paths:
            if path.is_symlink() or not path.is_file():
                raise ValueError("local non-symlink pre-fix source document required")
            if path.stat().st_size>1_000_000:
                raise ValueError("oversized source-era document")
        source_checks=(
            inspect_go43_local_pref_fix_document(paths[0].read_bytes()),
            inspect_go43_local_business_rules(paths[1].read_bytes()),
        )
        for field,checked in zip((
                "source_file_optional_external_witness",
                "business_rules_optional_external_witness"),source_checks):
            summary[field]={
                "stage":checked["stage"],
                "source_document_git_blob_sha40":
                    checked["source_document_git_blob_sha40"],
                "source_document_sha256":checked["source_document_sha256"],
                "source_document_byte_count":checked["source_document_byte_count"],
                "content_returned":False,
                "normative_approval_still_pending":True,
            }
    return summary


def main(argv=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-file",type=Path,default=None,
                        help="Optional trusted local pre-fix docs/design.md bytes")
    parser.add_argument("--business-rules-file",type=Path,default=None,
                        help="Local pre-fix docs/淮安80分业务规则.md: supply together with --source-file")
    parser.add_argument("--output",type=Path,default=None,
                        help="Optional PUBLIC status JSON; no source or oracle bytes")
    parser.add_argument("--require-admitted",action="store_true",
                        help="Fail exit 2 until an independent external runner approves")
    args=parser.parse_args(argv)
    report=compile_go43_public_handoff(
        source_file=args.source_file,business_rules_file=args.business_rules_file)
    blob=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.output is not None:
        out=args.output
        if (out.is_symlink() or
                args.source_file is not None and
                out.resolve()==args.source_file.resolve() or
                args.business_rules_file is not None and
                out.resolve()==args.business_rules_file.resolve()):
            raise ValueError("public status must not overwrite private/source input")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(blob,encoding="utf-8")
    print(blob,end="")
    return 2 if args.require_admitted else 0


if __name__=="__main__":
    raise SystemExit(main())
