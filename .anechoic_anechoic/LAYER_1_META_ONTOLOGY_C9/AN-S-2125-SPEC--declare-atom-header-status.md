---
identity:
  atom_id: AN-S-2125
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 6
  updated_at: '2026-11-20T17:25:38.351511+00:00'
---
## Summary

Declare Atom.Status

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.State.Status

## Claim

### Prose Claim

A Status with a dedicated folder has one integer Status Order Number from 0 through 999. Order numbers are distinct across Status values. Declare each number once, including for a Status admitted by several Roles. Active uses its Container's base directory.

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
    value_cardinality=1,
    property_occurrence_cardinality=1,
)
```
