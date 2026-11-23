---
atom_family: SPEC
atom_id: AN-S-2730
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 22:47:24 +0400
---

## Summary

Declare IS_INVERSE_ALIAS_FOR

## Claim

### Prose Claim

IS_INVERSE_ALIAS_FOR binds an inverse alias model address to its canonical Relation model address. The inverse alias is introduced by the canonical Relation Declaration and is not a separate Relation entity or Declaration. Normalizing an inverse alias to its canonical Relation swaps the written endpoints and their cardinality slots, preserving the numeric bounds. Explicit reverse writing of an inverse alias reverses its endpoints and slots again. Both writings refer to the same fact. This binding infers no bounds, grants no endpoint permission and creates no second authored Relation fact.

### Formal Claim

```CFEL
# model
$host ((IS_INVERSE_ALIAS_FOR)) $target
```

## Semantics

IS_INVERSE_ALIAS_FOR relates an inverse alias address to its canonical Relation address.
