---
atom_family: SPEC
atom_id: AN-S-2194
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T23:01:34.041979+00:00"
---


## Summary

Declare Workflow.Purpose

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Purpose",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom/(.Header.Context.Role := Operations)/Workflow",
    value_format=str,
    value_cardinality=1,
)
```
