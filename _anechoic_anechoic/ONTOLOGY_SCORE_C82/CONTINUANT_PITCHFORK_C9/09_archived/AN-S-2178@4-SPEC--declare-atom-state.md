---
atom_family: SPEC
atom_id: AN-S-2178
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 4
  updated_at: '2026-11-20T17:25:38.351511+00:00'
---


## Summary

Declare Atom.State

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.State

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='State',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header',
    value_format=object,
    value_cardinality=0,
    property_occurrence_cardinality=1,
    allowed_dependent_property_names=('Status', 'Version', 'Updated At'),
    ordered_dependent_property_pairs=(('Status', 'Version'), ('Version', 'Updated At')),
)
```
