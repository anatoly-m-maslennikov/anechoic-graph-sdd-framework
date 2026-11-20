---
atom_family: SPEC
atom_id: AN-S-3176
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T17:52:02.120155+00:00'
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
    base_path='Node//Artifact//Atom//Ticket Atom.Header.Context', value_format=str | None, field_options={'default': None, 'kw_only': True})
```

### Meaning

The optional Label supports navigation in Workbench and derived filenames.
The Template defines the Ticket kind.
