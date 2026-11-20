---
atom_family: SPEC
atom_id: AN-S-2066
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Atom.Header.Ref ID

## Claim

### Prose Claim

For an Atom in the Current or Backlog Status Group, Ref ID is its base Atom ID. For an Archived Atom, Ref ID is `<ID>@<Version>`. For a Draft Atom, Ref ID is `<ID>@<Version>-draft`.

### Formal Claim

```python
# model
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Ref ID',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Identity',
    property_occurrence_cardinality=1,
    value_cardinality=1,
    value_format='str',
    dependent_property_cardinality=0,
)
```
