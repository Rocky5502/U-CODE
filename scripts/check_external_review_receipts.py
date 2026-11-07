"""Local-only detached reviewer-signature integrity checker (NO ADMISSION).

Private, independently governed evidence files, verifier keys and signatures
must NEVER be put in public GitHub Actions, git commits, issue comments,
Overleaf, prompts, or published reproducibility archives.

An offline caller-selected trust registry is not itself independently
authenticated. This script cannot attest human independence, source rights,
hidden oracle custody, sandbox safety or task eligibility; there is no
execution authorization command. It only checks Ed25519 signatures on
canonical immutable evidence *claims* and prints a REDACTED status.
"""
from __future__ import annotations

import argparse
from dataclasses import fields
from datetime import datetime, timezone
import json
from pathlib import Path

from ucode.external_admission_receipt import (
    ExternalTaskBinding,ExternalGateSignature,TrustedExternalSigner,
    verify_external_evidence_claims,
)
from ucode.pilot_preflight import build_pilot_preflight

_MAX_INPUT=256*1024


def _object_no_dupes(pairs):
    result={}
    for k,v in pairs:
        if k in result:
            raise ValueError("duplicate private external evidence JSON field")
        result[k]=v
    return result


def _no_nan(text):
    raise ValueError("NaN/Infinity are not JSON evidence")


def _strict_payload(cls, obj):
    if type(obj) is not dict or set(obj)!={
            f.name for f in fields(cls) if f.name!="schema_version"
        } and set(obj)!={f.name for f in fields(cls)}:
        raise ValueError("unexpected/missing evidence envelope fields")
    return cls(**obj)


def _read_private(path: Path):
    p=Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError("private source must be local regular non-symlink file")
    content=p.read_bytes()
    if not content or len(content)>_MAX_INPUT:
        raise ValueError("private evidence file empty or overlong")
    try:
        return json.loads(
            content.decode("utf-8"),
            object_pairs_hook=_object_no_dupes,parse_constant=_no_nan
        )
    except (UnicodeError,json.JSONDecodeError) as exc:
        raise ValueError("invalid UTF-8 or JSON evidence file") from exc


def audit_private_detached_claims(
    binding_path: Path, receipt_path: Path,
    trust_policy_path: Path, verification_time_utc: str
) -> dict:
    paths=[Path(p) for p in (binding_path,receipt_path,trust_policy_path)]
    if len({p.resolve() for p in paths})!=3:
        raise ValueError("three independent offline evidence sources required")
    binding=_strict_payload(ExternalTaskBinding,_read_private(paths[0]))
    receipts_raw=_read_private(paths[1])
    if type(receipts_raw) is not list:
        raise ValueError("detached receipt JSON requires an array")
    receipts=tuple(_strict_payload(ExternalGateSignature,v)
                   for v in receipts_raw)
    trusted_raw=_read_private(paths[2])
    if type(trusted_raw) is not list:
        raise ValueError("external trust policy requires a signer array")
    keys=tuple(_strict_payload(TrustedExternalSigner,v)
               for v in trusted_raw)
    trust={}
    for signer in keys:
        if signer.key_id in trust:
            raise ValueError("duplicate verifier key ID in trust policy")
        trust[signer.key_id]=signer
    return verify_external_evidence_claims(
        binding,receipts,trust,
        prospective_pilot=build_pilot_preflight(),
        verification_time_utc=verification_time_utc,
    )


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding",type=Path,required=True)
    parser.add_argument("--receipts",type=Path,required=True)
    parser.add_argument("--trusted-public-keys",type=Path,required=True)
    parser.add_argument("--verification-time-utc",default=None,
                        help="UTC ISO8601 Z time; defaults to local machine UTC")
    parser.add_argument("--output",type=Path,default=None,
                        help="Optional REDACTED status-only JSON output path")
    parser.add_argument("--require-authorized",action="store_true",
                        help="Exit status 2: local signature checks cannot authorize tasks")
    args=parser.parse_args(argv)
    utc=args.verification_time_utc or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    result=audit_private_detached_claims(
        args.binding,args.receipts,args.trusted_public_keys,utc)
    text=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output is not None:
        out=args.output
        if (out.is_symlink() or out.resolve() in {
                args.binding.resolve(),args.receipts.resolve(),
                args.trusted_public_keys.resolve()}):
            raise ValueError("redacted output cannot overwrite private inputs")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(text,encoding="utf-8")
    print(text,end="")
    return 2 if args.require_authorized else 0


if __name__=="__main__":
    raise SystemExit(main())
