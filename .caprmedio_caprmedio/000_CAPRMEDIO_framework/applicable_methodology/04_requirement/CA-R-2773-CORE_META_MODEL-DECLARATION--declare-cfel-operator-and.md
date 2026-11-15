---
atom_id: CA-R-2773
ref_id: CA-R-2773
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ CFEL <+ Operator//Conjunction
tier: 3
status: active
version: 3
updated_at: '2026-11-13T05:29:51.943464+00:00'
carrier_destination:
  file:
    name: CA-R-2773-CORE_META_MODEL-DECLARATION--declare-cfel-operator-and.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2773-CORE_META_MODEL-DECLARATION--declare-cfel-operator-and.md
  source_atom_id: CA-R-2773
  source_atom_revision: 3
  source_sha256: 6d77bd485a653b71b03814d9496438928054e577341b218aee73099f0227efbf
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare CFEL operator AND

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Conjunction', value='"AND"')
```

## Semantics

Both Boolean operands must be true. Parenthesize mixed AND/OR expressions to make grouping explicit.
