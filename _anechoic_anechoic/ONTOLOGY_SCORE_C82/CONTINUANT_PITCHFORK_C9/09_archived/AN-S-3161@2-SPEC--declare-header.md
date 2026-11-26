---
atom_family: SPEC
atom_id: AN-S-3161
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-21T19:15:01.888027+00:00'
---

## Summary

Declare Header

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Header', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom', value_format=object, value_cardinality=0, property_occurrence_cardinality=1, allowed_dependent_property_names=('Atom Family', 'Atom ID', 'Concern', 'Container', 'Tier', 'Priority', 'Context', 'Relations', 'State'), ordered_dependent_property_pairs=(('Atom Family', 'Atom ID'), ('Atom ID', 'Concern'), ('Concern', 'Container'), ('Container', 'Tier'), ('Tier', 'Priority'), ('Priority', 'Context'), ('Context', 'Relations'), ('Relations', 'State')))
```
