---
identity:
  atom_id: AN-S-2700
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 9
  updated_at: '2026-11-13T22:57:39.635646+00:00'
---
## Summary

Define int Value Format

## Claim

### Prose Claim


The int Value Format admits integer numeric values with no fractional part. It
does not set a numeric range, cardinality, uniqueness rule, or carrier
representation.



### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ValueFormat

class IntegerValueFormat(ValueFormat):
    pass

declare_entity(entity_name='int', entity_class=IntegerValueFormat)
```

## Semantics

int is the value domain selected by an `[int]` annotation on one direct
Property value.
