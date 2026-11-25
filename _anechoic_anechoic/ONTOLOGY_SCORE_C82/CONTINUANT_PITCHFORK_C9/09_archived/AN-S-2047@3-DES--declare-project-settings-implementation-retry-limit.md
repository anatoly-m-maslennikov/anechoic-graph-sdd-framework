---
atom_family: SPEC
atom_id: AN-S-2047
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T23:03:12.990249+00:00"
---

## Summary

Declare Project.Settings.Implementation Retry Limit

## Claim

### Prose Claim


An omitted value follows the governed default resolution. A value is an integer at least zero. Zero permits no retries after the initial failure. The limit does not grant repair permission or bypass authority or confidence rules.

### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Implementation Retry Limit',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    value_format='int',
    dependent_property_cardinality=0,
)
```

