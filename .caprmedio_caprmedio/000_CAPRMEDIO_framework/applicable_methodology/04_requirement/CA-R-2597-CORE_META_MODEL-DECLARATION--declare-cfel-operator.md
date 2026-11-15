---
atom_id: CA-R-2597
ref_id: CA-R-2597
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ CFEL<+Operator//ExpressionSeparator
tier: 3
status: active
version: 3
updated_at: '2026-11-13T05:28:34.204151+00:00'
carrier_destination:
  file:
    name: CA-R-2597-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2597-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
  source_atom_id: CA-R-2597
  source_atom_revision: 3
  source_sha256: 1140d0f0f22a937bff0acc420f8eeb79a80735818fdfd505d3e7e1d0153ba744
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare CFEL operator ;

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//ExpressionSeparator', value='";"')
```

## Semantics

Separate complete CFEL expressions with `;`; a line break is layout only. Read contiguous `<;` and `;>` as Property-order tokens, not as the standalone separator.
