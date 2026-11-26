---
atom_family: SPEC
atom_id: AN-S-4805
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: '2026-11-24T11:19:56.257484+00:00'
---

## Summary

Declare Spec Atom Status

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom.Header.State.Status

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Status',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header.State',
    value_format=str,
    field_options={'kw_only': True},
    allowed_values=('draft', 'ready', 'active', 'archived'),
    value_cardinality=1,
    property_occurrence_cardinality=1,
    applies_to_entity_classes=('Node//Artifact//Atom//Spec Atom',),
)
```
