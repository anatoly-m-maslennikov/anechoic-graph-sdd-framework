---
atom_family: SPEC
atom_id: AN-S-2589
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 3
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---
## Summary

Declare Atom.Updated At

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.State.Updated At

## Claim

### Prose Claim

The Updated At value equals the maximum happened_at among Event Records whose single object_output has a version, has this Atom ID and current Version, and has action create or update.

### Formal Claim

```python
from datetime import datetime
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Updated At',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.State',
    value_format=datetime | None,
    field_options={'default': None, 'kw_only': True},
)
```

