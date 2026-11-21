---
atom_family: SPEC
atom_id: AN-S-2789
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: '2026-11-13T22:57:39.635646+00:00'
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
