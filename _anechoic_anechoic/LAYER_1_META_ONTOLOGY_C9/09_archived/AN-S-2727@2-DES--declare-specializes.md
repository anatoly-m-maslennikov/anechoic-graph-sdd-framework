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
  version: 2
  updated_at: 2026-11-04 19:46:41 +0400
---

## Summary

Declare SPECIALIZES

## Claim

### Prose Claim

The child Atom's Claim is more specific or stricter than the parent Atom's Claim in the same or a narrower Scope and preserves the parent's applicable constraints. A conditional specialization is included. A reference or dependency alone does not establish SPECIALIZES.

### Formal Claim

```CFEL
# model
Relation//SPECIALIZES ((HAS_INVERSE)) Relation//IS_SPECIALIZED_BY;

Relation//SPECIALIZES ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom//$child ((SPECIALIZES)) Atom//$parent
```

## Semantics

SPECIALIZES relates a child Atom to the Atom whose Claim it specializes.
