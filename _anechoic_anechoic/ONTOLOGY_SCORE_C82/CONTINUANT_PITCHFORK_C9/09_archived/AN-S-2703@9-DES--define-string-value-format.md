---
atom_family: SPEC
atom_id: AN-S-2703
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 9
  updated_at: "2026-11-25T22:46:54.878344+00:00"
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
from anechoic.formal_claims import declare_entity
from anechoic.model import ValueFormat

class StringValueFormat(ValueFormat):
    pass

declare_entity(entity_name='string', entity_class=StringValueFormat)
```

## Semantics

string is the value domain selected by a `[string]` annotation on one direct
Property value.
