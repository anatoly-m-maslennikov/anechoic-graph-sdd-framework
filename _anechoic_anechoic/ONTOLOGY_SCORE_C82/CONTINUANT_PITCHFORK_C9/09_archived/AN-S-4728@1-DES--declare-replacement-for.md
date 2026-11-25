---
atom_family: SPEC
atom_id: AN-S-4728
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-08 15:22:04 +0400
---

## Summary

Declare REPLACEMENT_FOR

## Claim

### Prose Claim

The Host is a replacement Atom. The Target is a predecessor Atom identified by its base Atom ID. One replacement can target several predecessors.

A Draft Host proposes replacement. Its links remain after promotion, including when the predecessor becomes Archived. Completed replacement requires an adopted successor and an Archived predecessor.

### Formal Claim

```CFEL
# model
Relation//REPLACEMENT_FOR ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
$replacement[<Atom>] ((REPLACEMENT_FOR)) $predecessor[<Atom>]
```

## Semantics

REPLACEMENT_FOR relates a replacement Atom to the predecessor Atom whose contribution it replaces.
