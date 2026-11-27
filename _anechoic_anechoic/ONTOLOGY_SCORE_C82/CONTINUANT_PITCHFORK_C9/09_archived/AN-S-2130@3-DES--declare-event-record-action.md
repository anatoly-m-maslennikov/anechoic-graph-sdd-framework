---
atom_family: SPEC
atom_id: AN-S-2130
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T09:25:50.934388+00:00"
---
## Summary

Declare Event Record.action

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='action',
    relation_name="IS_PROPERTY_OF",
    base_path='Event Record',
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
    allowed_values=('create', 'update', 'archive'),
)
```

