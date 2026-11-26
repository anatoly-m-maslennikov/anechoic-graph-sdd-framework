---
atom_family: SPEC
atom_id: AN-S-3163
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T21:44:52.683584+00:00'
---

## Summary

Declare Concern

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Concern

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Concern', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header', value_format=object, value_cardinality=0, property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), allowed_dependent_property_names=('Subject', 'Path', 'Relation'), ordered_dependent_property_pairs=(('Subject', 'Path'), ('Path', 'Relation')))
```
