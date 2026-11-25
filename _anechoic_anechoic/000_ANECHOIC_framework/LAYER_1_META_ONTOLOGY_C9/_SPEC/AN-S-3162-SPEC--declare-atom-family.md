---
atom_family: SPEC
atom_id: AN-S-3162
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T17:25:38.351511+00:00'
---

## Summary

Declare Atom Family

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Atom Family

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Atom Family', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header', value_format=str, value_cardinality=1, property_occurrence_cardinality=1, allowed_values=('SPEC', 'TKT', 'PROJECT_CONFIG'))
```
