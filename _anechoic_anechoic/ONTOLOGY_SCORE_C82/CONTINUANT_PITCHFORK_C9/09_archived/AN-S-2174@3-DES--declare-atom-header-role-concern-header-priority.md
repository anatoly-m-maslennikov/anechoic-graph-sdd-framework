---
atom_family: SPEC
atom_id: AN-S-2174
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T19:32:46.467975+00:00"
---

## Summary

Declare Atom/(.Header.Role := Concern).Header.Priority

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Priority",
    relation_name="IS_PROPERTY_OF",
    base_path='Atom/(.Header.Context.Role:=Concern).Header.Context.Concern',
    property_occurrence_cardinality=1,
    value_format="str",
    value_cardinality=1,
    dependent_property_cardinality=0,
    allowed_values=("High", "Medium", "Low"),
)
```
