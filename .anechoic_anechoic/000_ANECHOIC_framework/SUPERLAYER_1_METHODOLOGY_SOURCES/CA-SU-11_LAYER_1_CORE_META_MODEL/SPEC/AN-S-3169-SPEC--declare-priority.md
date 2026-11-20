---
atom_family: SPEC
atom_id: AN-S-3169
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T17:25:38.351511+00:00'
---

## Summary

Declare Priority

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Ticket Atom.Header.Structure.Priority

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Priority', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Ticket Atom.Header.Structure', value_format=int, field_options={'default': 2, 'kw_only': True})
```
