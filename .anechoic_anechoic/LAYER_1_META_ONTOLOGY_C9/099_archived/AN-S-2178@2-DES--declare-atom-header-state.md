---
identity:
  atom_id: AN-S-2178
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-13T00:27:04.807824+00:00'
---


## Summary

Declare Atom.Header.State

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='State',
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header",
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=3,
    allowed_dependent_property_names=('Status', 'Version', 'Updated At'),
    ordered_dependent_property_pairs=(('Status', 'Version'), ('Version', 'Updated At')),
)
```
