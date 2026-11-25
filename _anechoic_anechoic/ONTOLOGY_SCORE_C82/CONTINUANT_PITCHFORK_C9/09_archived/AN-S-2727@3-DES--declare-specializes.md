---
atom_family: SPEC
atom_id: AN-S-2727
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-05 18:23:39 +0400
---

## Summary

Declare SPECIALIZES

## Claim

### Prose Claim

The child Atom's Claim is more specific or stricter than the parent Atom's Claim in the same or a narrower Scope and preserves the parent's applicable constraints. A conditional specialization is included. A reference or dependency alone does not establish SPECIALIZES. IS_SPECIALIZED_BY is the inverse alias, with parent and child endpoints reversed.

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
