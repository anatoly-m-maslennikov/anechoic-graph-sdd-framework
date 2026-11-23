---
atom_family: SPEC
atom_id: AN-S-2733
container:
  component: C9
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-08 20:06:37 +0400
---

## Summary

Declare IS_REPLACEMENT_FOR

## Claim

### Prose Claim

The Host is a replacement Atom. The Target is a predecessor Atom identified by its base Atom ID. One replacement can target several predecessors.

A Draft Host proposes replacement. Its links remain after promotion, including when the predecessor becomes Archived. Completed replacement requires an adopted successor and an Archived predecessor.

### Formal Claim

```CFEL
# model
Relation//IS_REPLACEMENT_FOR ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
$replacement[<Atom>] ((IS_REPLACEMENT_FOR)) $predecessor[<Atom>]
```

## Semantics

IS_REPLACEMENT_FOR relates a replacement Atom to the predecessor Atom whose contribution it replaces.
