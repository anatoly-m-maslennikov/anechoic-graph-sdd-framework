---
identity:
  atom_id: AN-S-3164
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

Declare Subject

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Concern.Subject

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Subject', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header.Concern', value_format=str | None, value_cardinality=1, property_occurrence_cardinality=1, field_options={'default': None, 'kw_only': True})
```
