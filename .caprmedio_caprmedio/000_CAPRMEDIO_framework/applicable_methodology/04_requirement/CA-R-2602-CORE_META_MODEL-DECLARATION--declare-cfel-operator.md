---
atom_id: CA-R-2602
ref_id: CA-R-2602
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ CFEL<+Operator//ImmediateWildcard
tier: 3
status: active
version: 2
updated_at: '2026-11-13T05:28:49.418850+00:00'
carrier_destination:
  file:
    name: CA-R-2602-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2602-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
  source_atom_id: CA-R-2602
  source_atom_revision: 2
  source_sha256: c20b448d217fd71db67d6a584ea41dd6b8b0d1ec6668a41236a07b569ca9d1ca
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare CFEL operator *

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//ImmediateWildcard', value='"*"')
```

## Semantics

Select immediate dependent Properties in `p.*`.
