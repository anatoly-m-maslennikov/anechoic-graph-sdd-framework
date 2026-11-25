---
atom_family: SPEC
atom_id: AN-S-2702
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 9
  updated_at: "2026-11-25T22:46:54.588540+00:00"
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
