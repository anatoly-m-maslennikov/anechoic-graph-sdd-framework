---
identity:
  atom_id: AN-S-2061
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

Declare Atom.Header.Container.scope_unit

## Claim

### Prose Claim

The value is the stable ID of the containing Scope Unit.
### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='scope_unit',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Context.Container',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    value_format='str',
    dependent_property_cardinality=0,
)
```

