---
identity:
  atom_id: AN-S-2710
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 8
  updated_at: '2026-11-12T21:29:37.101539+00:00'
---
## Summary

Define Relation Name

## Claim

### Prose Claim


Relation Name is the canonical name of a reusable Relation Type.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Name",
    relation_name="IS_PROPERTY_OF",
    base_path="Relation",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
