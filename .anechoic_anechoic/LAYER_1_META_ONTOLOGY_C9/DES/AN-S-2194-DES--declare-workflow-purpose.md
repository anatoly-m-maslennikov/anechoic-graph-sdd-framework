---
identity:
  atom_id: AN-S-2194
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-13T00:03:26.251582+00:00'
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
