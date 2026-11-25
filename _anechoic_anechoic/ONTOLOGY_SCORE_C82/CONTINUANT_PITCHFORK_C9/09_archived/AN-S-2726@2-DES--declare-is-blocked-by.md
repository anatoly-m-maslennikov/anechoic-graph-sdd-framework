---
atom_family: SPEC
atom_id: AN-S-2726
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 16:52:59 +0400
---

## Summary

Declare IS_BLOCKED_BY

## Claim

### Prose Claim

A dependent Plan may start only after each Plan it is blocked by is Done.

### Formal Claim

```CFEL
# model
Relation//IS_BLOCKED_BY ((HAS_INVERSE)) Relation//BLOCKS;

Relation//IS_BLOCKED_BY ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom/(.Header.Context.Role: Plan)//$dependent ((IS_BLOCKED_BY)) Atom/(.Header.Context.Role: Plan)//$prerequisite
```

## Semantics

IS_BLOCKED_BY relates a dependent Plan to a prerequisite Plan.
