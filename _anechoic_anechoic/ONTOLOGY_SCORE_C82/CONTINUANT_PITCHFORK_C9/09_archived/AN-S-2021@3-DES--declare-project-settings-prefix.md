---
atom_family: SPEC
atom_id: AN-S-2021
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T19:32:46.789758+00:00"
---

## Summary

Declare Project Settings Prefix

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Prefix',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    value_format=str,
    property_occurrence_cardinality=1,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

