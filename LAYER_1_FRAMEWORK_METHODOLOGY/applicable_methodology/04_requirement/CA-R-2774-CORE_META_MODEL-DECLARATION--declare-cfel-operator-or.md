---
atom_id: CA-R-2774
ref_id: CA-R-2774
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ CFEL <+ Operator//Disjunction
tier: 3
status: active
version: 3
updated_at: '2026-11-13T05:29:54.280355+00:00'
carrier_destination:
  file:
    name: CA-R-2774-CORE_META_MODEL-DECLARATION--declare-cfel-operator-or.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2774-CORE_META_MODEL-DECLARATION--declare-cfel-operator-or.md
  source_atom_id: CA-R-2774
  source_atom_revision: 3
  source_sha256: d60a87571f72c7fd41d84de0789d3253b2a5b45d320e6756e72d235bfb03d2b3
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare CFEL operator OR

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Disjunction', value='"OR"')
```

## Semantics

At least one Boolean operand must be true. Parenthesize mixed AND/OR expressions to make grouping explicit.
