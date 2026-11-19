---
atom_id: CA-E-462
ref_id: CA-E-462
container:
  scope_unit: CA-SU-11
role: Evaluation
form: Eval Policy
topics:
  main_subject: ANECHOIC_MODEL <+ Event Record
  dependencies:
  - ANECHOIC_MODEL <+ Atom.Header.Identity.ID
  - ANECHOIC_MODEL <+ Atom.Header.State.Version
  - ANECHOIC_MODEL <+ Carrier
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)
  - ANECHOIC_MODEL <+ Journal
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Projection
tier: 3
relations:
  evaluation_for:
  - CA-R-1491
  - CA-R-807
status: Active
version: 33
updated_at: 2026-11-02 08:06:47 +0400
carrier_destination:
  file:
    name: CA-E-462-CORE_META_MODEL-EVAL_POLICY--validate-atom-replacement-event-evidence.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation/CA-E-462-CORE_META_MODEL-EVAL_POLICY--validate-atom-replacement-event-evidence.md
  source_atom_id: CA-E-462
  source_atom_revision: 33
  source_sha256: dd9c7fd1d48b9bf684d65a419e4971d65e06f92be8f8d0104a3c716f25758d5c
  original_relations_sha256: 80acf3d6005192a1209f2dc66b2cd8a4c44c2f3761556ba982dc7cd5b06bcdb6
---
## Summary

Validate Atom replacement event evidence

## Claim

### Prose Claim


Atom replacement event evidence.


an Event Record offered as Atom replacement evidence **must** undergo an actual Evaluation against CA-R-807. Available evidence and Journal acceptance are **not** proof that the replacement is correct.

## Details

### Checks

the Evaluation of that Event Record **must** run and report a passing, failed, or unresolved result. It **must**:

- report a failed replacement result **if** predecessor **or** successor identities are missing, unresolved, duplicate, self-referencing, **or** mismatched;
- verify that **every** named successor was Active **before** the predecessor was archived, that the archived predecessor preserves its body, Summary, identity, numeric Version, and prior Updated At, with only archived Status changed on its Archive Carrier; verify retained exact prior Revision bytes, including the prior Version, Status **and** Updated At, and that **`=1`** authoritative Journal Event Record records that replacement;
- distinguish selected Carrier representation evidence from proof of replacement correctness; and
- treat repeated submission of the same Event Record as non-evidence of another authoritative record.

### Failure disposition

an Event Record whose actual Evaluation reports failure **or** uncertainty **must not** be treated as a conforming replacement merely because the Journal preserves it under CA-R-1491. Its correction disposition **must** route a governed-source change through its authorized Workflow and **must not** rewrite accepted history.

this Evaluation **must not** require a Git Commit **or** a particular Journal serialization. Available evidence without the performed Evaluation and its reported result is **not** a passing result.
