---
atom_id: CA-R-2603
ref_id: CA-R-2603
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ CFEL<+Operator//Inequality
tier: 3
status: active
version: 2
updated_at: '2026-11-13T05:28:54.447472+00:00'
carrier_destination:
  file:
    name: CA-R-2603-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2603-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
  source_atom_id: CA-R-2603
  source_atom_revision: 2
  source_sha256: 41bb516cccf8a08551a8c133199a0b8768f85ee00be2f93d468e783b59f6be50
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare CFEL operator !=

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Inequality', value='"!="')
```

## Semantics

Test inequality between resolved values.
