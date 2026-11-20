---
identity:
  atom_id: AN-S-2128
context:
  container:
    component: C9
  tier: 4
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T18:59:51.161573+00:00'
---

## Summary

Declare legacy Operation content

## Claim

### Prose Claim

An Operations Atom may retain its legacy Operation section during migration. Operation is a Markdown Content Property. Its presentation subheadings, lists and code blocks remain part of its value.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Operation',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Content',
    applies_to_entity_classes=['Operations'],
    value_format='markdown',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
)
```

## Semantics

Operation is the operation text carried by the legacy Operations Atom. This declaration describes that existing section; it does not decide whether a later Form must use Operation or Claim.
