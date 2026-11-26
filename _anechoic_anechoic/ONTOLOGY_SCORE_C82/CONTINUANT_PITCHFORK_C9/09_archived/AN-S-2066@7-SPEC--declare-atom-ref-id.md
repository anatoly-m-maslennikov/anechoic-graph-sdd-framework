---
atom_family: SPEC
atom_id: AN-S-2066
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 7
  updated_at: '2026-11-20T17:25:38.351511+00:00'
---

## Summary

Declare Atom.Ref ID

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Ref ID

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Ref ID',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom',
    value_format=str,
    value_cardinality=1,
    property_occurrence_cardinality=1,
    derived_from_properties=('Header.Atom ID', 'Header.State.Version', 'Header.State.Status'),
)
```

### Prose Claim

Ref ID is computed on read and is not persisted.
