---
atom_family: SPEC
atom_id: AN-S-3298
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: '2026-11-22T00:29:11.818654+00:00'
---

## Summary

Declare Atom encapsulation

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Encapsulation

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Encapsulation',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom',
    value_format=str,
    allowed_values=('white_box', 'black_box'),
    field_options={'class_var': True, 'default': 'white_box'},
)
```

### Prose Claim

Encapsulation describes whether the Atom addresses the implementation
or behavior observable through its interfaces.
