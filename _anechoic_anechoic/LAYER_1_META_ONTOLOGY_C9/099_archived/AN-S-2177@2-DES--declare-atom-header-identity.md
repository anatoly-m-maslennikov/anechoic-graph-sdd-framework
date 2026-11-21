---
atom_family: SPEC
atom_id: AN-S-2177
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-13T00:27:02.702771+00:00'
---


## Summary

Declare Atom.Header.Identity

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Identity',
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header",
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=2,
    allowed_dependent_property_names=('ID', 'Ref ID'),
    ordered_dependent_property_pairs=(('ID', 'Ref ID'),),
)
```
