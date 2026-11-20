---
identity:
  atom_id: AN-S-3128
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Tier

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose//Component Purpose.Tier

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Tier',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Spec Atom',
    value_format=int,
    field_options={'kw_only': True},
    allowed_values=(0,),
    value_cardinality=1,
    property_occurrence_cardinality=1,
    applies_to_entity_classes=('Node//Artifact//Atom//Spec Atom//Purpose//Component Purpose',),
)
```
