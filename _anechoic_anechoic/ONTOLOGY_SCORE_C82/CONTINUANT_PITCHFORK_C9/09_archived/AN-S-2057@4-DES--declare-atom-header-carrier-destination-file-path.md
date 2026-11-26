---
atom_family: SPEC
atom_id: AN-S-2057
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Atom.Header.Carrier Destination.File.Path

## Claim

### Prose Claim




Calculated path of the containing directory, relative to the repository root.
### Formal Claim

```python
# model
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Path',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Destination.File',
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

