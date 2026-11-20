---
identity:
  atom_id: AN-S-2000
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 17
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Project.Framework Settings.Artifact Timestamp Timezone

## Claim

### Prose Claim


the Artifact timestamp timezone setting in Framework Settings.


The value supplies the timezone used when emitting Artifact timestamps.


### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Artifact Timestamp Timezone',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    value_format='str',
    dependent_property_cardinality=0,
)
```

## Details

Evidence: CA-D-390 supplies the timezone interpretation and its concrete encoding. Candidate #6 keeps Settings attached to Project and keeps concrete ANECHOIC mechanisms in Project Configuration. This definition adds no format, allowed value or default; those remain separate Delivery rules.
