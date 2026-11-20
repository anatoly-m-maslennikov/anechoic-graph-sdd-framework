---
identity:
  atom_id: AN-S-2041
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-12T17:23:54+00:00'
---

## Summary

Define Semantic Resolution Threshold

## Claim

### Prose Claim


A present threshold value is an integer-percentage override. An absent override uses the governed default.

### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Semantic Resolution Threshold',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings.Confidence',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
)
```

