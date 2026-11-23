---
atom_family: SPEC
atom_id: AN-S-2042
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T17:23:54+00:00'
---

## Summary

Define Interaction Reporting Mode

## Claim

### Formal Claim

```python
# model
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Reporting Mode',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings.Interaction',
    property_occurrence_cardinality=1,
    value_cardinality=1,
    value_format='str',
    dependent_property_cardinality=0,
)
```

