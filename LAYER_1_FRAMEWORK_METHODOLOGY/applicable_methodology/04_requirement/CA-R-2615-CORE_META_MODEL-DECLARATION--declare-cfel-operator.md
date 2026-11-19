---
atom_id: CA-R-2615
ref_id: CA-R-2615
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ CFEL<+Operator//SubjectValueSelection
tier: 3
status: active
version: 2
updated_at: '2026-11-13T05:29:42.684007+00:00'
carrier_destination:
  file:
    name: CA-R-2615-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2615-CORE_META_MODEL-DECLARATION--declare-cfel-operator.md
  source_atom_id: CA-R-2615
  source_atom_revision: 2
  source_sha256: 1be4551ad79c3f2a3617ac44aa707dc6c6e4ed3d77c87d9bd993ad358abaf737
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare CFEL operator :=

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//SubjectValueSelection', value='":="')
```

## Semantics

In a Subject or a filtered Node expression in a Formal Claim, combine an admitted Property value with selection; for example, `Workflow/(.Purpose := Runtime)`. It is not assignment.
