---
atom_family: SPEC
atom_id: AN-S-3129
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 4
  updated_at: '2026-11-22T22:23:08.810817+00:00'
---

## Summary

Declare Tier

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract//Component Contract.Header.Tier

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Tier',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Spec Atom.Header',
    value_format=int,
    field_options={'kw_only': True},
    allowed_values=(0,),
    value_cardinality=1,
    property_occurrence_cardinality=1,
    applies_to_entity_classes=('Node//Artifact//Atom//Spec Atom//Contract//Component Contract',),
)
```
