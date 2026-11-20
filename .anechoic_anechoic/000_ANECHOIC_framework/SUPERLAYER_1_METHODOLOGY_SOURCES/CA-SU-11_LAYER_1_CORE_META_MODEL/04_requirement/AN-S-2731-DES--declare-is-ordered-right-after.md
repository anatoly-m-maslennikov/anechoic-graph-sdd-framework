---
identity:
  atom_id: AN-S-2731
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-14T07:33:24.792510+00:00'
---
## Summary

Declare IS_ORDERED_RIGHT_AFTER

## Claim

### Prose Claim

IS_ORDERED_RIGHT_AFTER relates Atom Header or Content Property instances. The Host immediately follows the Target in sibling order. The inverse alias IS_ORDERED_RIGHT_BEFORE reads the same link in reverse.

`x ;> y` means x is immediately before y, in the order x; y. `x <; y` means x is immediately after y, in the order y; x.


### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_ORDERED_RIGHT_AFTER',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom.Header.**', 'Atom.Content.**')},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom.Header.**', 'Atom.Content.**')},
    inverse_alias='IS_ORDERED_RIGHT_BEFORE',
    written_alias='<;',
    reverse_written_alias=';>',
)
```

## Semantics

IS_ORDERED_RIGHT_AFTER relates a Property instance to its immediately preceding sibling.
