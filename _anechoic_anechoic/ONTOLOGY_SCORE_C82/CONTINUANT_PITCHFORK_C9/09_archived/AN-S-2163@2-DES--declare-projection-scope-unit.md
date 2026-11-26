---
atom_family: SPEC
atom_id: AN-S-2163
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T22:43:31.685047+00:00"
---

## Summary

Declare Projection.Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name="Scope Unit",
    relation_name="IS_PROPERTY_OF",
    base_path="Projection",
    property_occurrence_cardinality=1,
    value_format=ScopeUnit,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

