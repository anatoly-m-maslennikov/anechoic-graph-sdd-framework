---
atom_family: SPEC
atom_id: AN-S-3131
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Lens Whitelist

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest.Lens Whitelist

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Lens Whitelist',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Spec Atom//Manifest',
    value_format=list[str] | None,
    field_options={'default': None, 'kw_only': True},
)
```
