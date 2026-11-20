---
identity:
  atom_id: AN-S-2198
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-13T03:59:30.052668+00:00'
---
## Summary

Declare Project.Settings.AI Agent Confidence Threshold

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="AI Agent Confidence Threshold",
    relation_name="IS_PROPERTY_OF",
    base_path="Project.Settings",
    property_occurrence_cardinality=1,
    value_format=int,
    value_cardinality=1,
    dependent_property_cardinality=0,
    minimum_value=0,
    maximum_value=100,
    fallback_value=90,
)
```

