---
atom_family: SPEC
atom_id: AN-S-3176
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-21T15:48:18+00:00'
---

## Summary

Declare the Ticket Atom navigation Label

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Ticket Atom.Header.Context.Label

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
declare_entity(entity_name='Label', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Ticket Atom.Header.Context', value_format=str | None,
    allowed_values=('Task', 'Subtask', 'Sub-epic', 'Epic', 'Version'),
    field_options={'default': None, 'kw_only': True})
```

### Meaning

Planning Tickets use the Task Template. The optional Label supports navigation
in Workbench and derived filenames. It does not set containment or lifecycle
rules. Extend the vocabulary here when a new navigation label is needed.
