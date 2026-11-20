---
identity:
  atom_id: AN-S-3171
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T17:25:38.351511+00:00'
---

## Summary

Declare Template

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Context.Template

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Template', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header.Context', value_format=str | None, field_options={'default': None, 'kw_only': True})
```
