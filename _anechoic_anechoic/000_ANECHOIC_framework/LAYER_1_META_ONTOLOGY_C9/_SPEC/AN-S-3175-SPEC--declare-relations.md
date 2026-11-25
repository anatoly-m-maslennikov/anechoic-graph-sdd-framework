---
atom_family: SPEC
atom_id: AN-S-3175
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

Declare Relations

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Relations

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Relations', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header', value_format=dict[str, list[str]] | None, value_cardinality=0, property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), dependent_property_cardinality=Cardinality(minimum=1, maximum=None), dependent_property_value_format=str, dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None), field_options={'default': None, 'kw_only': True})
```
