---
atom_family: SPEC
atom_id: AN-S-2701
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 9
  updated_at: '2026-11-13T22:57:39.635646+00:00'
---
## Summary

Define float Value Format

## Claim

### Prose Claim


The float Value Format admits floating-point numeric values. It does not set
precision, a numeric range, cardinality, uniqueness, or carrier
representation.



### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ValueFormat

class FloatValueFormat(ValueFormat):
    pass

declare_entity(entity_name='float', entity_class=FloatValueFormat)
```

## Semantics

float is the value domain selected by a `[float]` annotation on one direct
Property value.
