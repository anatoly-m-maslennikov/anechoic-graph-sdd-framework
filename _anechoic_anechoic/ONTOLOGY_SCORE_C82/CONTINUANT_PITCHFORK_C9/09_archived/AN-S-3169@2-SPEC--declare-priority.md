---
atom_family: SPEC
atom_id: AN-S-3169
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-21T19:14:35.061068+00:00'
---

## Summary

Declare Priority

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Ticket Atom.Header.Priority

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Priority', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Ticket Atom.Header', value_format=int, value_cardinality=1, property_occurrence_cardinality=1, field_options={'kw_only': True})
```
