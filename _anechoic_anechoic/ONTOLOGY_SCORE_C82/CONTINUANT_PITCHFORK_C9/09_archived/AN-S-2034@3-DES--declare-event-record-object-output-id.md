---
atom_family: SPEC
atom_id: AN-S-2034
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T09:25:49.689857+00:00"
---
## Summary

Declare Event Record.object_output.id

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='id',
    relation_name='IS_PROPERTY_OF',
    base_path='Event Record.object_output',
    value_format=str,
    property_occurrence_cardinality=1,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

