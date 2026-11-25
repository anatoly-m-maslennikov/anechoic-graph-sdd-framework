---
atom_family: SPEC
atom_id: AN-S-2597
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T22:57:24.985880+00:00'
---
## Summary

Declare Event Record.Relations

## Claim

### Prose Claim

Each immediate dependent Property name is a Relation instance (Relation//$relation).

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Relations',
    relation_name="IS_PROPERTY_OF",
    base_path='Event Record',
    property_occurrence_cardinality=1, value_cardinality=0, dependent_property_cardinality=Cardinality(minimum=0, maximum=None),
)
```
