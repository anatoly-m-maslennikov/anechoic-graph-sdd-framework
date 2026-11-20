---
atom_family: SPEC
atom_id: AN-S-2019
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 9
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Project.Settings

## Claim

### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Settings',
    relation_name='IS_PROPERTY_OF',
    base_path='Project',
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=3, maximum=11),
    allowed_dependent_property_names=('Name', 'Prefix', 'AI Agent Confidence Threshold', 'Artifact Timestamp Timezone', 'Code-Root Locators', 'Confidence', 'Framework Control-Root Locator', 'Interaction', 'Authority Modes', 'Implementation Retry Limit', 'RMED Review'),
)
```

