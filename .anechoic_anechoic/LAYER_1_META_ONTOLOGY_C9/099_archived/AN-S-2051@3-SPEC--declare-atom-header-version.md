---
identity:
  atom_id: AN-S-2051
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 3
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---
## Summary

Declare Atom.Version

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.State.Version

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Version',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.State',
    value_format=int,
    minimum_value=1,
    value_cardinality=1,
    property_occurrence_cardinality=1,
)
```
