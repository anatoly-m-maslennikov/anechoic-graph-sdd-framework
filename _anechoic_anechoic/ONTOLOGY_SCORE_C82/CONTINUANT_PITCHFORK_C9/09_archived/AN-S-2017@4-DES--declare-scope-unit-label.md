---
atom_family: SPEC
atom_id: AN-S-2017
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T20:23:23.380475+00:00"
---

## Summary

Declare Scope Unit Label

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Label',
    relation_name='IS_PROPERTY_OF',
    base_path='Scope Unit',
    value_format=str,
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
)
```

