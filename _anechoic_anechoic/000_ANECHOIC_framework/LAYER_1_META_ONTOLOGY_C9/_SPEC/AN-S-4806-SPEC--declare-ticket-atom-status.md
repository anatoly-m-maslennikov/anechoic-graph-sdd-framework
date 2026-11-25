---
atom_family: SPEC
atom_id: AN-S-4806
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-24T11:19:56.257484+00:00'
---

## Summary

Declare Ticket Atom Status

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Ticket Atom.Header.State.Status

## Claim

### Prose Claim

For Ticket Atoms, `active` is accepted for compatibility with existing carriers. The Ticket lifecycle defines publication and status changes.

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
    allowed_values=('draft', 'backlog', 'in_queue', 'done', 'canceled', 'resolved', 'complete', 'archived', 'active'),
    value_cardinality=1,
    property_occurrence_cardinality=1,
    applies_to_entity_classes=('Node//Artifact//Atom//Ticket Atom',),
)
```
