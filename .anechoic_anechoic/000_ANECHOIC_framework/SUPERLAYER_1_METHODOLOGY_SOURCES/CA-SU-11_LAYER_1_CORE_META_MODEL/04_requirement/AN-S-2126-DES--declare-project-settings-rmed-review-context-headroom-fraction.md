---
identity:
  atom_id: AN-S-2126
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T19:06:43.021656+00:00'
---

## Summary

Declare Project.Settings.RMED Review.Context Headroom Fraction

## Claim

### Prose Claim


When present, the value is finite and strictly between zero and one.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Context Headroom Fraction",
    relation_name="IS_PROPERTY_OF",
    base_path="Project.Settings.RMED Review",
    value_format=float,
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
)
```

