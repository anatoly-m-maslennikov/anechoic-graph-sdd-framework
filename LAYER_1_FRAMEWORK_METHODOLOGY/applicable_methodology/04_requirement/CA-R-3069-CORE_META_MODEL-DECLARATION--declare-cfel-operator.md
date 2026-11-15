---
atom_id: CA-R-3069
ref_id: CA-R-3069
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ CFEL<+Operator//AllowedValue
tier: 3
relations:
  is_replacement_for:
  - CA-R-2592
status: active
version: 2
updated_at: '2026-11-13T07:06:24.288117+00:00'
carrier_destination:
  file:
    name: CA-R-3069-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3069-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
  source_atom_id: CA-R-3069
  source_atom_revision: 2
  source_sha256: cee0681badc58e7aeeb061d5b0359c3a782b528e9061dff41a32a11a9de64753
  original_relations_sha256: 15aab09df7f07e5df5dd2dd71f76db3b94fada59b31221c35df7f0f330c8899f
---

## Summary

Declare CFEL operator ::

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//AllowedValue', value='"::"')
```

## Semantics

In `X :: Y`, a literal Y admits one allowed value of the complete qualified Property address X. A bracketed right operand supplies a Format constraint.
