---
identity:
  atom_id: AN-S-2065
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T17:23:54+00:00'
---

## Summary

Declare Workflow.Content.Claim.Formal Claim

## Claim

### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Formal Claim',
    relation_name='IS_PROPERTY_OF',
    base_path='Workflow.Content.Claim',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=1,
    value_format='markdown',
    dependent_property_cardinality=0,
)
```
