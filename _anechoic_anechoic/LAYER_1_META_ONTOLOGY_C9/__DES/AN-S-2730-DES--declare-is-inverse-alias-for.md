---
atom_family: SPEC
atom_id: AN-S-2730
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare IS_INVERSE_ALIAS_FOR

## Claim

### Prose Claim

IS_INVERSE_ALIAS_FOR binds an inverse alias model address to its canonical Relation model address. The inverse alias is introduced by the canonical Relation Declaration and is not a separate Relation entity or Declaration. Normalizing an inverse alias to its canonical Relation swaps the written endpoints and their cardinality slots, preserving the numeric bounds. Explicit reverse writing of an inverse alias reverses its endpoints and slots again. Both writings refer to the same fact. This binding infers no bounds, grants no endpoint permission and creates no second authored Relation fact.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_INVERSE_ALIAS_FOR',
    source_endpoint={'level': 'model_entities',
 'entity_paths': ('Relation',),
 'address_form': 'inverse_alias'},
    target_endpoint={'level': 'model_entities', 'entity_paths': ('Relation',), 'address_form': 'canonical'},
    swap_endpoints=True,
    swap_endpoint_cardinalities=True,
)
```

## Semantics

IS_INVERSE_ALIAS_FOR relates an inverse alias address to its canonical Relation address.
