---
identity:
  atom_id: AN-S-2049
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Atom.Header.Role

## Claim


### Prose Claim

Role Order Number classifies the Role-qualified Atom kind in the Model. Each Role Declaration assigns exactly one positive integer. Order numbers are distinct across Roles. Gaps are allowed.

### Formal Claim

```python
# model
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Role',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Context',
    property_occurrence_cardinality=1,
    value_cardinality=1,
    value_format='str',
    dependent_property_cardinality=0,
)
```
