---
atom_family: SPEC
atom_id: AN-S-3168
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

Declare Container

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Structure.Container

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Container', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header.Structure', value_format=dict[str, str], value_cardinality=1, property_occurrence_cardinality=1)
```
