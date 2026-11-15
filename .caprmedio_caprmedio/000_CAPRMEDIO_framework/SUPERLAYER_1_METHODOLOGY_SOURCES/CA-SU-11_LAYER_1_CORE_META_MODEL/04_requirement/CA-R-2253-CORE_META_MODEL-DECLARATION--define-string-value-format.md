---
atom_id: CA-R-2253
ref_id: CA-R-2253
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Format/string
  dependencies:
  - CAPRMEDIO_MODEL <+ Format
tier: 1
status: active
version: 9
updated_at: '2026-11-13T22:57:39.635646+00:00'
carrier_destination:
  file:
    name: CA-R-2253-CORE_META_MODEL-DECLARATION--define-string-value-format.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Define string Value Format

## Claim

### Prose Claim


The string Value Format admits textual string values. It does not turn null
into a string or set a property's cardinality, uniqueness, or carrier
representation.



### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import ValueFormat

class StringValueFormat(ValueFormat):
    pass

declare_entity(entity_name='string', entity_class=StringValueFormat)
```

## Semantics

string is the value domain selected by a `[string]` annotation on one direct
Property value.
