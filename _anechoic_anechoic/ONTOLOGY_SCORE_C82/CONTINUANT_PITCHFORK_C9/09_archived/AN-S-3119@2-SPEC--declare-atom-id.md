---
atom_family: SPEC
atom_id: AN-S-3119
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 2
  updated_at: '2026-11-20T16:02:18.721582+00:00'
---

## Summary

Declare Atom ID

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Identity.Atom ID

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Atom ID',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Identity',
    value_format=str,
    value_cardinality=1,
    property_occurrence_cardinality=1,
)
```
