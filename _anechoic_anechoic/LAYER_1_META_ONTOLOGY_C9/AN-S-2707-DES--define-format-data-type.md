---
atom_family: SPEC
atom_id: AN-S-2707
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 6
  updated_at: '2026-11-12T21:16:49.823331+00:00'
---
## Summary

Define Format Data Type

## Claim

### Prose Claim


Format Data Type names the admissible value domain of a direct Property value.
It is separate from cardinality. The initial vocabulary is provisional; list,
map and reference semantics remain with the governing Format definition.



### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Data Type",
    relation_name="IS_PROPERTY_OF",
    base_path="Format",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
