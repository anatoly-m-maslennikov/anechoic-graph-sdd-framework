---
atom_family: SPEC
atom_id: AN-S-2043
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T23:09:46.563848+00:00"
---

## Summary

Declare Project.Settings.RMED Review.Max Atoms

## Claim

### Prose Claim


When present, the value is positive. Its absence supplies no default.

### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Max Atoms',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings.RMED Review',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    value_format='int',
    dependent_property_cardinality=0,
)
```

