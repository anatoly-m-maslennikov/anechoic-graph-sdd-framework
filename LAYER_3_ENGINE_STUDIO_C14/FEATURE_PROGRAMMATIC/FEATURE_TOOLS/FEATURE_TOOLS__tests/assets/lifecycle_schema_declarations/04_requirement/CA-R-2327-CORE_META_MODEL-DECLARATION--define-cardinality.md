---
atom_id: CA-R-2327
ref_id: CA-R-2327
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Cardinality
tier: 1
status: active
version: 8
updated_at: '2026-11-13T22:57:39.635646+00:00'
carrier_destination:
  file:
    name: CA-R-2327-CORE_META_MODEL-DECLARATION--define-cardinality.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Define Cardinality

## Claim

### Prose Claim

Cardinality specifies an allowed count. Bounds are inclusive non-negative
integers. An unspecified maximum permits any count at or above the minimum.

- A Property occurrence count measures the presence of that named Property on
  one bearer. An explicit occurrence bound governs presence. Otherwise a
  positive value minimum requires a leaf Property.
- A direct-value count measures values on one Property occurrence. A structural
  parent can hold dependent Properties with zero direct values.
- A dependent Property count measures distinct declared children on one
  bearer. An immediate count includes one level. A recursive count includes
  every descendant level.
- The two Relation endpoint counts are independent. Each counts matching
  links per selected endpoint. Reading the inverse swaps the endpoint counts.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class CardinalityContract:
    pass

declare_entity(entity_name='Cardinality', entity_class=CardinalityContract)
```
