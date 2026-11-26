---
atom_family: SPEC
atom_id: AN-S-3170
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T17:25:38.351511+00:00'
---

## Summary

Declare Context

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Context

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Context', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header', value_format=object, value_cardinality=0, property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), allowed_dependent_property_names=('Template', 'Lens'), ordered_dependent_property_pairs=(('Template', 'Lens'),))
```
