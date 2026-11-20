---
atom_family: SPEC
atom_id: AN-S-3172
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

Declare Template

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Ticket Atom.Header.Context.Template

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Template', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header.Context', value_format=str, property_occurrence_cardinality=1, field_options={'kw_only': True}, applies_to_entity_classes=('Node//Artifact//Atom//Ticket Atom',))
```
