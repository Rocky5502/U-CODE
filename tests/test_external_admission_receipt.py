"""Adversarial synthetic Ed25519 reviewer claims; NO real human signatures.

Private keys are ephemeral and generated IN MEMORY during unit tests.
Neither signatures, keys, hidden oracles nor completed reviewer forms are
committed as external attestation or source-era task approval.
"""
from dataclasses import replace,asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
import io
from scripts.check_external_review_receipts import audit_private_detached_claims,main as cli
from copy import deepcopy
from hashlib import sha256
import json
import unittest

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
    _CRYPTO=True
except ImportError:
    _CRYPTO=False

from ucode.external_admission_receipt import (
    ExternalTaskBinding,ExternalGateSignature,TrustedExternalSigner,
    assert_binding_matches_frozen_pilot,verify_external_evidence_claims,
    _ROLES,_SIGNATURE_DOMAIN,
)
from ucode.pilot_preflight import build_pilot_preflight
from ucode.task_admission import REQUIRED_GATES

ISSUED="2026-11-06T12:00:00Z"
CHECK="2026-11-07T12:00:00Z"
EXPIRES="2027-01-01T12:00:00Z"


def dummy_hash(name):
    return sha256(("INVENTED UNIT TEST "+name).encode("utf-8")).hexdigest()


@unittest.skipUnless(_CRYPTO,"optional [admission] cryptography extra needed")
class SyntheticExternalReviewReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pilot=build_pilot_preflight()
        cls.pr=next(x for x in cls.pilot["candidates"]
                    if x["candidate_id"]==104)

    def binding(self,**changes):
        row=self.pr
        fields={
            "candidate_id":row["candidate_id"],
            "repository":row["repository"],
            "pr_url":row["pr_url"],
            "task_base_sha40":row["immutable_pre_fix_base_sha40"],
            "task_scope":row["task_scope"],
            "prospective_dossier_sha256":row["dossier_sha256"],
            "source_era_spec_sha256":dummy_hash("unverified spec"),
            "independent_oracle_commitment_sha256":dummy_hash("unsealed oracle"),
            "sandbox_image_digest":"sha256:"+dummy_hash("unapproved image"),
            "toolchain_lock_sha256":dummy_hash("unverified toolchain"),
            "resource_meter_profile_sha256":dummy_hash("unmeasured meter"),
            "repo_lineage_split_sha256":dummy_hash("unapproved lineage"),
            "rights_decision_sha256":dummy_hash("unapproved rights"),
        }
        fields.update(changes)
        return ExternalTaskBinding(**fields)

    def synthetic_reviewers(self,binding=None):
        binding=self.binding() if binding is None else binding
        signers={}
        private={}
        for role in sorted(set(_ROLES.values())):
            for slot in ("A","B"):
                key_id=role+"."+slot
                key=Ed25519PrivateKey.generate()
                private[key_id]=key
                pub=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
                signers[key_id]=TrustedExternalSigner(
                    key_id=key_id, public_key_hex=pub.hex(),
                    gate_role=role,reviewer_slot=slot)
        receipts=[]
        for gate in REQUIRED_GATES:
            for slot in ("A","B"):
                key_id=_ROLES[gate]+"."+slot
                record=ExternalGateSignature(
                    candidate_id=binding.candidate_id,gate=gate,
                    reviewer_slot=slot,signer_key_id=key_id,
                    binding_sha256=binding.binding_sha256,
                    evidence_sha256=dummy_hash("synthetic "+gate),
                    issued_at_utc=ISSUED,expires_at_utc=EXPIRES,
                    signature_hex="0"*128)
                receipts.append(replace(
                    record,signature_hex=private[key_id].sign(
                        record.message_bytes()).hex()
                ))
        return tuple(receipts),signers

    def audit(self,binding=None,receipts=None,signers=None,**extra):
        binding=binding if binding is not None else self.binding()
        default_receipts,default_signers=self.synthetic_reviewers(binding)
        return verify_external_evidence_claims(
            binding, default_receipts if receipts is None else receipts,
            default_signers if signers is None else signers,
            prospective_pilot=extra.get("pilot",self.pilot),
            verification_time_utc=extra.get("when",CHECK))

    def test_two_independently_keyed_reviews_per_gate_cannot_admit_task(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        result=self.audit(binding,signed,signers)
        self.assertEqual(result["signed_claims_verified"],16)
        self.assertEqual(result["reviewed_evidence_gates"],8)
        self.assertTrue(result["all_signatures_valid_under_supplied_keys"])
        self.assertFalse(result["scientific_task_admitted"])
        self.assertFalse(result["external_code_execution_authorized"])
        self.assertFalse(result["external_human_identity_independently_attested"])
        self.assertFalse(result["sealed_oracle_independently_attested"])
        self.assertFalse(result["physical_sandbox_independently_attested"])

    def test_public_status_omits_signer_keys_evidence_and_private_details(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        result=self.audit(binding,signed,signers)
        summary=json.dumps(result)
        self.assertNotIn("public_key_hex",summary)
        self.assertNotIn("signature_hex",summary)
        self.assertNotIn("signer_key_id",summary)
        self.assertNotIn(signed[0].evidence_sha256,summary)
        self.assertNotIn("oracle_commitment",summary)
        self.assertNotIn("source_era_spec",summary)

    def test_valid_signature_wrong_claim_rejected(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        changed=list(signed)
        changed[0]=replace(changed[0],evidence_sha256=dummy_hash("tampered"))
        with self.assertRaisesRegex(ValueError,"invalid detached"):
            self.audit(binding,tuple(changed),signers)

    def test_valid_signature_but_new_task_digest_cannot_be_replayed(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        mutated=self.binding(rights_decision_sha256=dummy_hash("new rights"))
        with self.assertRaisesRegex(ValueError,"different immutable task context"):
            self.audit(mutated,signed,signers)

    def test_source_repository_and_base_sha_bound_to_frozen_metadata(self):
        binding=self.binding()
        with self.assertRaisesRegex(ValueError,"source-era PR dossier"):
            assert_binding_matches_frozen_pilot(
                replace(binding,task_base_sha40="f"*40),self.pilot)
        with self.assertRaisesRegex(ValueError,"PR must match"):
            replace(binding,pr_url="https://github.com/another/repo/pull/3")

    def test_reviewer_role_cannot_sign_another_gate(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        changed=dict(signers)
        current=signed[0]
        changed[current.signer_key_id]=replace(
            changed[current.signer_key_id],gate_role="resource_meters")
        with self.assertRaisesRegex(ValueError,"gate role"):
            self.audit(binding,signed,changed)

    def test_reviewer_slot_must_match_policy(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        changed=dict(signers)
        current=signed[0]
        changed[current.signer_key_id]=replace(
            changed[current.signer_key_id],reviewer_slot="B")
        with self.assertRaisesRegex(ValueError,"reviewer slot"):
            self.audit(binding,signed,changed)

    def test_pubkey_alias_across_roles_is_rejected(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        changed=dict(signers)
        k1,k2=list(changed)[:2]
        changed[k2]=replace(changed[k2],
                            public_key_hex=changed[k1].public_key_hex)
        with self.assertRaisesRegex(ValueError,"aliased verifier"):
            self.audit(binding,signed,changed)

    def test_missing_and_duplicate_signed_records_rejected(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        for bad in (signed[:-1],signed[:-1]+signed[:1]):
            with self.assertRaises(ValueError):
                self.audit(binding,bad,signers)

    def test_one_untrusted_key_cannot_claim_admission(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        changed=dict(signers)
        del changed[signed[0].signer_key_id]
        with self.assertRaisesRegex(ValueError,"untrusted signer"):
            self.audit(binding,signed,changed)

    def test_expired_future_or_reversed_timestamp_rejected(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        for when in ("2026-11-05T12:00:00Z","2027-01-01T12:00:00Z"):
            with self.subTest(when=when),self.assertRaisesRegex(
                    ValueError,"not valid at verification time"):
                self.audit(binding,signed,signers,when=when)
        with self.assertRaisesRegex(ValueError,"expires before issue"):
            replace(signed[0],expires_at_utc="2026-01-01T00:00:00Z")
        with self.assertRaisesRegex(ValueError,"UTC reviewer"):
            replace(signed[0],issued_at_utc="2026-13-99T12:00:00Z")

    def test_old_signature_cannot_be_repurposed_for_other_gate_or_role(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        changed=list(signed)
        changed[0]=replace(changed[0],gate="resource_limits")
        with self.assertRaises(ValueError):
            self.audit(binding,tuple(changed),signers)

    def test_binding_alone_does_not_prove_oracle_or_license(self):
        b=self.binding()
        self.assertEqual(len(b.binding_sha256),64)
        self.assertIn(b"source_era_spec_sha256",b.canonical_bytes())
        self.assertIn(b"independent_oracle_commitment_sha256",b.canonical_bytes())
        self.assertNotIn(b"independent_oracle_commitment_sha256",
                         _SIGNATURE_DOMAIN)
        self.assertNotEqual(
            b.binding_sha256,
            replace(b,source_era_spec_sha256=dummy_hash("different")).binding_sha256)
        self.assertNotEqual(
            b.binding_sha256,
            replace(b,resource_meter_profile_sha256=dummy_hash("different")).binding_sha256)

    def test_schema_rejects_fake_sandbox_mutable_image_or_missing_hash(self):
        b=self.binding()
        with self.assertRaisesRegex(ValueError,"OCI SHA256"):
            replace(b,sandbox_image_digest="ubuntu:latest")
        with self.assertRaisesRegex(ValueError,"lower-case"):
            replace(b,toolchain_lock_sha256="f"*63)
        with self.assertRaisesRegex(ValueError,"schema"):
            replace(b,schema_version="ucode-fake-v2")

    def test_context_rejects_self_promoted_public_pilot(self):
        b=self.binding()
        pilot=deepcopy(self.pilot)
        pilot["qualified_executable_tasks"]=1
        with self.assertRaisesRegex(ValueError,"self-promoted"):
            assert_binding_matches_frozen_pilot(b,pilot)
        pilot=deepcopy(self.pilot)
        pilot["candidates"][1]["independently_qualified"]=True
        with self.assertRaisesRegex(ValueError,"unapproved"):
            assert_binding_matches_frozen_pilot(b,pilot)

    def test_unknown_trust_roster_and_bad_signature_format_fail_closed(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        with self.assertRaisesRegex(ValueError,"external signer registry"):
            self.audit(binding,signed,{})
        with self.assertRaisesRegex(ValueError,"64 bytes"):
            replace(signed[0],signature_hex="z"*128)

    def test_different_order_same_canonical_binding_fingerprint(self):
        binding=self.binding()
        serialized=binding.canonical_bytes()
        self.assertEqual(serialized,
                         binding.canonical_bytes())
        self.assertEqual(binding.binding_sha256,sha256(serialized).hexdigest())
        self.assertTrue(serialized.startswith(b'{"candidate_id":'))

    def fixture_files(self,tmp,binding=None,receipts=None,signers=None):
        b=binding if binding is not None else self.binding()
        r,k=self.synthetic_reviewers(b)
        r=r if receipts is None else receipts
        k=k if signers is None else signers
        names=("binding.json","review_claims.json","keys.json")
        payloads=(asdict(b),[asdict(x) for x in r],
                  [asdict(x) for x in k.values()])
        paths=[Path(tmp,n) for n in names]
        for p,value in zip(paths,payloads):
            p.write_text(json.dumps(value,sort_keys=True)+"\n",encoding="utf-8")
        return paths

    def test_private_cli_can_verify_synthetic_signatures_and_redact(self):
        with TemporaryDirectory() as tmp:
            binding,claims,keys=self.fixture_files(tmp)
            output=Path(tmp,"public_status.json")
            with redirect_stdout(io.StringIO()) as sink:
                self.assertEqual(cli([
                    "--binding",str(binding),"--receipts",str(claims),
                    "--trusted-public-keys",str(keys),
                    "--verification-time-utc",CHECK,
                    "--output",str(output)
                ]),0)
            report=json.loads(output.read_text())
            self.assertEqual(report["signed_claims_verified"],16)
            self.assertFalse(report["scientific_task_admitted"])
            self.assertFalse(report["external_code_execution_authorized"])
            self.assertEqual(sink.getvalue(),output.read_text())
            self.assertNotIn("signer_key_id",sink.getvalue())
            self.assertNotIn("signature_hex",sink.getvalue())
            self.assertNotIn("source_era_spec_sha256",sink.getvalue())

    def test_cli_explicit_auth_required_stays_blocked_after_valid_signatures(self):
        with TemporaryDirectory() as tmp:
            binding,claims,keys=self.fixture_files(tmp)
            with redirect_stdout(io.StringIO()) as sink:
                code=cli([
                    "--binding",str(binding),"--receipts",str(claims),
                    "--trusted-public-keys",str(keys),
                    "--verification-time-utc",CHECK,
                    "--require-authorized"
                ])
            self.assertEqual(code,2)
            self.assertIn('"scientific_task_admitted": false',sink.getvalue())

    def test_private_cli_cannot_overwrite_trust_input(self):
        with TemporaryDirectory() as tmp:
            binding,claims,keys=self.fixture_files(tmp)
            original=keys.read_bytes()
            with redirect_stdout(io.StringIO()),self.assertRaisesRegex(
                    ValueError,"cannot overwrite private"):
                cli(["--binding",str(binding),"--receipts",str(claims),
                    "--trusted-public-keys",str(keys),
                    "--verification-time-utc",CHECK,"--output",str(keys)])
            self.assertEqual(keys.read_bytes(),original)

    def test_cli_refuses_duplicate_json_fields_and_unknown_approval(self):
        with TemporaryDirectory() as tmp:
            binding,claims,keys=self.fixture_files(tmp)
            data=json.loads(binding.read_text())
            data["authorized_for_experiment"]=True
            binding.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"unexpected/missing"):
                audit_private_detached_claims(binding,claims,keys,CHECK)
            data.pop("authorized_for_experiment")
            contents=json.dumps(data)
            contents=contents[:-1]+',"candidate_id":104}'
            binding.write_text(contents,encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"duplicate private"):
                audit_private_detached_claims(binding,claims,keys,CHECK)

    def test_duplicate_two_slot_public_keys_for_same_role_fail(self):
        binding=self.binding()
        signed,signers=self.synthetic_reviewers(binding)
        a=next(x for x in signed if x.gate=="resource_limits"
               and x.reviewer_slot=="A")
        b=next(x for x in signed if x.gate=="resource_limits"
               and x.reviewer_slot=="B")
        signers=dict(signers)
        signers[b.signer_key_id]=replace(signers[b.signer_key_id],
            public_key_hex=signers[a.signer_key_id].public_key_hex)
        with self.assertRaisesRegex(ValueError,"aliased"):
            self.audit(binding,signed,signers)


if __name__=="__main__":
    unittest.main()
