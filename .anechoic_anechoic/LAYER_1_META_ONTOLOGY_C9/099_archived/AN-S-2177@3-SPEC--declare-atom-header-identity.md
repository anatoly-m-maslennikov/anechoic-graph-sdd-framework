---
identity:
  atom_id: AN-S-2177
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 3
  updated_at: '2026-11-20T16:02:18.721582+00:00'
---


## Summary

Declare Atom.Identity

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Identity

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Identity',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom',
    value_format=object,
    value_cardinality=0,
    property_occurrence_cardinality=1,
    allowed_dependent_property_names=('Atom ID',),
)
```
