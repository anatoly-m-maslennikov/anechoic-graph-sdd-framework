---
atom_family: SPEC
atom_id: AN-S-3120
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Family Marker

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Family Marker

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Family Marker',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom',
    value_format=str,
    field_options={'class_var': True, 'default': None},
)
```
