---
atom_family: SPEC
atom_id: AN-S-2023
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Projection.Source.Atoms

## Claim

### Prose Claim



Each value is an Atom ID with an explicit Version.
### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Atoms',
    relation_name='IS_PROPERTY_OF',
    base_path='Projection.Source',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=Cardinality(minimum=0, maximum=None),
    value_format='str',
    dependent_property_cardinality=0,
)
```

