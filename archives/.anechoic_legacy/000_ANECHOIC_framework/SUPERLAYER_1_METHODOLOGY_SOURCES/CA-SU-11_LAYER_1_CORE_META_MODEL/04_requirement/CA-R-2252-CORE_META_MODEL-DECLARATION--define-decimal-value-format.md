---
atom_id: CA-R-2252
ref_id: CA-R-2252
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Format/decimal
  dependencies:
  - ANECHOIC_MODEL <+ Format
tier: 1
status: active
version: 9
updated_at: '2026-11-13T22:57:39.635646+00:00'
carrier_destination:
  file:
    name: CA-R-2252-CORE_META_MODEL-DECLARATION--define-decimal-value-format.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
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
from anechoic.formal_claims import declare_entity
from anechoic.model import ValueFormat

class DecimalValueFormat(ValueFormat):
    pass

declare_entity(entity_name='decimal', entity_class=DecimalValueFormat)
```

## Semantics

decimal is the value domain selected by a `[decimal]` annotation on one direct
Property value.
