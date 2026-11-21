---
atom_family: SPEC
atom_id: AN-S-2033
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Declare Event Record.object_output

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='object_output',
    relation_name='IS_PROPERTY_OF',
    base_path='Event Record',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=2, maximum=3),
    allowed_dependent_property_names=('id', 'version', 'updated_at'),
)
```

