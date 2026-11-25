---
atom_family: SPEC
atom_id: AN-S-2055
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Declare Atom.Header.Carrier Destination.File

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='File',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Destination',
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=2,
    allowed_dependent_property_names=('Name', 'Path'),
    dependent_property_value_format=str,
)
```
