---
identity:
  atom_id: AN-S-2733
context:
  container:
    component: C9
  tier: 4
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare IS_REPLACEMENT_FOR

## Claim

### Prose Claim

The Host is a replacement Atom. The Target is a predecessor Atom identified by its base Atom ID. One replacement can target several predecessors.

A Draft Host proposes replacement. Its links remain after promotion, including when the predecessor becomes Archived. Completed replacement requires an adopted successor and an Archived predecessor.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_REPLACEMENT_FOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',), 'reference_form': 'base_atom_id'},
)
```

## Semantics

IS_REPLACEMENT_FOR relates a replacement Atom to the predecessor Atom whose contribution it replaces.
