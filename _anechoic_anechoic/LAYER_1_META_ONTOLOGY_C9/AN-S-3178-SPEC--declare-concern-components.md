---
atom_family: SPEC
atom_id: AN-S-3178
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T21:44:52.681755+00:00'
---

## Summary

Declare Concern Components

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Concern.Components

## Claim

### Prose Claim

List the distinct Component IDs declared in the Project that the Concern affects.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Components', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header.Concern', value_format=list[str],
    value_cardinality=Cardinality(minimum=1, maximum=None),
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    field_options={'default': None, 'kw_only': True})
```
