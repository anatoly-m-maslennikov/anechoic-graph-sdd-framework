---
atom_id: CA-R-2252
ref_id: CA-R-2252
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Format/decimal
  dependencies:
  - CAPRMEDIO_MODEL <+ Format
tier: 1
status: active
version: 9
updated_at: '2026-11-13T22:57:39.635646+00:00'
carrier_destination:
  file:
    name: CA-R-2252-CORE_META_MODEL-DECLARATION--define-decimal-value-format.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2252-CORE_META_MODEL-DECLARATION--define-decimal-value-format.md
  source_atom_id: CA-R-2252
  source_atom_revision: 9
  source_sha256: aefc68472ac22c05d76c87a70b8657211b3a1fbf8ed445e04035e8fc0fb35c1e
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define decimal Value Format

## Claim

### Prose Claim


The decimal Value Format admits decimal numeric values. It does not set scale,
precision, a numeric range, cardinality, uniqueness, or carrier
representation.



### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import ValueFormat

class DecimalValueFormat(ValueFormat):
    pass

declare_entity(entity_name='decimal', entity_class=DecimalValueFormat)
```

## Semantics

decimal is the value domain selected by a `[decimal]` annotation on one direct
Property value.
