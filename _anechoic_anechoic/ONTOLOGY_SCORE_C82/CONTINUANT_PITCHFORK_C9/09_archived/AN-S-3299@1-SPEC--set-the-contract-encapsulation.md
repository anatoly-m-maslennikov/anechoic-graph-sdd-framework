---
atom_family: SPEC
atom_id: AN-S-3299
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

Set the Contract encapsulation

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract.Encapsulation

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
    field_options={'class_var': True, 'default': 'black_box'},
    applies_to_entity_classes=('Node//Artifact//Atom//Spec Atom//Contract',),
)
```

### Prose Claim

A Contract describes externally observable behavior, including UI,
visual output, and programmatic I/O.
