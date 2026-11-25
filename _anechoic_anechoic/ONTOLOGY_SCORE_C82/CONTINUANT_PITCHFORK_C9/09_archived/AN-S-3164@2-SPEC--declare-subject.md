---
atom_family: SPEC
atom_id: AN-S-3164
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-20T21:44:52.684502+00:00'
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
    base_path='Node//Artifact//Atom.Header.Concern', value_format=str | None, value_cardinality=1, property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), field_options={'default': None, 'kw_only': True})
```
