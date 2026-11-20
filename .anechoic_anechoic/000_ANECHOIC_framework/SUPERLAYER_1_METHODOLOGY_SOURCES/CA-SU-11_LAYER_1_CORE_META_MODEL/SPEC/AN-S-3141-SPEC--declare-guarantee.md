---
identity:
  atom_id: AN-S-3141
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Guarantee

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract.Guarantee

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Guarantee',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Spec Atom//Contract',
    value_format=str,
    value_cardinality=1,
    property_occurrence_cardinality=1,
)
```
