---
atom_family: SPEC
atom_id: AN-S-2016
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T20:23:23.256052+00:00"
---

## Summary

Declare Scope Unit Name

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Name',
    relation_name='IS_PROPERTY_OF',
    base_path='Scope Unit',
    value_format=str,
    property_occurrence_cardinality=1,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

