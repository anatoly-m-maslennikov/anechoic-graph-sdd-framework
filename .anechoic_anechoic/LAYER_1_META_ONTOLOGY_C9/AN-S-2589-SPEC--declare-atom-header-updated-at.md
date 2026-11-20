---
identity:
  atom_id: AN-S-2589
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 4
  updated_at: '2026-11-20T14:52:48.784566+00:00'
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
    property_occurrence_cardinality=1,
    value_format=datetime,
    value_cardinality=1,
    field_options={'kw_only': True},
)
```

