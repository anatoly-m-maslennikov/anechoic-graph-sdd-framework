---
identity:
  atom_id: AN-S-2003
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

Define Project.Framework Settings.Framework Control-Root Locator

## Claim

### Prose Claim


the Project's framework control-root reference in Framework Settings.



### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Framework Control-Root Locator',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    value_format='str',
    dependent_property_cardinality=0,
)
```

## Details

Evidence: CA-D-370 requires the locator to resolve to the Directory Carrier prescribed by CA-D-317 without selecting another authority root. Candidate #6 keeps concrete ANECHOIC mechanisms in Project Configuration. This definition adds no path or alternative authority root; those remain Delivery rules.
