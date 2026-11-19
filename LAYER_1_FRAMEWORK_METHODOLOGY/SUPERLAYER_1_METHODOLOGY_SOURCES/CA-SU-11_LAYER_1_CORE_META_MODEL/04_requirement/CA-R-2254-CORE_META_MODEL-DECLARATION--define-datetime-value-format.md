---
atom_id: CA-R-2254
ref_id: CA-R-2254
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Format/datetime
  dependencies:
  - ANECHOIC_MODEL <+ Format
tier: 1
status: active
version: 9
updated_at: '2026-11-13T22:57:39.635646+00:00'
carrier_destination:
  file:
    name: CA-R-2254-CORE_META_MODEL-DECLARATION--define-datetime-value-format.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Define datetime Value Format

## Claim

### Prose Claim


The datetime Value Format admits date-and-time values. It does not set a
timezone convention, precision, cardinality, uniqueness, or carrier
representation.



### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ValueFormat

class DateTimeValueFormat(ValueFormat):
    pass

declare_entity(entity_name='datetime', entity_class=DateTimeValueFormat)
```

## Semantics

datetime is the value domain selected by a `[datetime]` annotation on one
direct Property value.
