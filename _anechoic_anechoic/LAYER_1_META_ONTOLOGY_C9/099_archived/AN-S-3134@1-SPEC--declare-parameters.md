---
atom_family: SPEC
atom_id: AN-S-3134
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Parameters

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest.Parameters

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Parameters',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest',
    value_format=dict[str, object],
    field_options={'default_factory': 'dict'},
)
```
