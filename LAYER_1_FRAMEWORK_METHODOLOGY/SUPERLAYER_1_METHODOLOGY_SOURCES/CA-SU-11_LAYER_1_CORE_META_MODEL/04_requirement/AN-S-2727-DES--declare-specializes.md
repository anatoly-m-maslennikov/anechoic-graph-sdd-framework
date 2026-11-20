---
identity:
  atom_id: AN-S-2727
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-14T07:33:58.659369+00:00'
---
## Summary

Declare SPECIALIZES

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="SPECIALIZES",
    source_endpoint={"level": "instances", "entity_paths": ("Atom",)},
    target_endpoint={"level": "instances", "entity_paths": ("Atom",)},
    inverse_alias="IS_SPECIALIZED_BY",
)
```

## Semantics

SPECIALIZES relates a child Atom to the Atom whose Claim it specializes.
