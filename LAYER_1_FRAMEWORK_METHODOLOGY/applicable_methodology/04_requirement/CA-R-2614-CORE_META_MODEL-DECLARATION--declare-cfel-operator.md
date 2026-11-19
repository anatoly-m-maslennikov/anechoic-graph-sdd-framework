---
atom_id: CA-R-2614
ref_id: CA-R-2614
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ CFEL<+Operator//SelectionExclusion
tier: 3
status: active
version: 2
updated_at: '2026-11-13T05:29:39.474702+00:00'
carrier_destination:
  file:
    name: CA-R-2614-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2614-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
  source_atom_id: CA-R-2614
  source_atom_revision: 2
  source_sha256: dabd41e72dd028036f56dd14bce7373b95c07d0ca9a6b40fa2fb2bab34a324e2
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare CFEL operator !()

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//SelectionExclusion', value='"!()"')
```

## Semantics

Exclude selected branches from a delivery selection.
