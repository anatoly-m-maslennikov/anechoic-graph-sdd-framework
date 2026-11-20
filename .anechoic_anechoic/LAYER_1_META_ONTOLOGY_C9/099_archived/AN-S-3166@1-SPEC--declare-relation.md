---
atom_family: SPEC
atom_id: AN-S-3166
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-20T21:44:52.688079+00:00"
---

## Summary

Declare Relation

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Concern.Relation

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Relation', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header.Concern', value_format=str | None, value_cardinality=1, property_occurrence_cardinality=1, field_options={'default': None, 'kw_only': True})
```
