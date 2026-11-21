---
atom_family: SPEC
atom_id: AN-S-2178
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 3
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---


## Summary

Declare Atom.State

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.State

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='State',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom',
    value_format=object,
    value_cardinality=0,
    property_occurrence_cardinality=1,
    allowed_dependent_property_names=('Version', 'Status', 'Updated At'),
)
```
