---
atom_family: SPEC
atom_id: AN-S-2699
structure:
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

Define bool Value Format

## Claim

### Prose Claim


The bool Value Format admits the Boolean values true and false. It does not set a
property's cardinality, default, nullability, or carrier representation.



### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ValueFormat

class BooleanValueFormat(ValueFormat):
    pass

declare_entity(entity_name='bool', entity_class=BooleanValueFormat)
```

## Semantics

bool is the value domain selected by a `[bool]` annotation on one direct
Property value.
