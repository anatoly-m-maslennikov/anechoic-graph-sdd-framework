---
atom_id: CA-R-3062
ref_id: CA-R-3062
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Step.Inputs
tier: 3
status: active
version: 3
updated_at: '2026-11-12T23:10:06.505246+00:00'
carrier_destination:
  file:
    name: CA-R-3062-CORE_META_MODEL-DECLARATION--declare-step-inputs.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3062-CORE_META_MODEL-DECLARATION--declare-step-inputs.md
  source_atom_id: CA-R-3062
  source_atom_revision: 3
  source_sha256: af5aab9472eb24ea4b32f556d3bc6fe354d3e38478efd145e084838784d500f5
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Step.Inputs

## Claim

### Prose Claim

Step Inputs are optional. They identify the input values used by the Step; bindings supply values.

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

declare_entity(entity_name='Inputs', relation_name="IS_PROPERTY_OF", base_path='Atom/(.Header.Context.Role:=Operations)/Step')
```
