---
atom_family: SPEC
atom_id: AN-S-2704
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 9
  updated_at: "2026-11-25T22:46:55.263892+00:00"
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
