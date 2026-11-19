---
atom_id: CA-R-2608
ref_id: CA-R-2608
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ CFEL<+Operator//Membership
tier: 3
status: active
version: 2
updated_at: '2026-11-13T05:29:16.220257+00:00'
carrier_destination:
  file:
    name: CA-R-2608-CORE_META_MODEL-DECLARATION--declare-cfel-operator-in-not-in.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2608-CORE_META_MODEL-DECLARATION--declare-cfel-operator-in-not-in.md
  source_atom_id: CA-R-2608
  source_atom_revision: 2
  source_sha256: c7ed92ec2d2014cb3c04e03c98baaf764960f348bfe8cc40cae2b3364817ab35
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare CFEL operator in / not in

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Membership', value='"in / not in"')
```

## Semantics

Test membership or non-membership in a selected set.
