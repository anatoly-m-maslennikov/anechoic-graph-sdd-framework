---
atom_family: SPEC
atom_id: AN-S-2872
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 16:33:24 +0400
---

## Summary

Declare IS_VALUE_CONSTRAINT_OF

## Claim

### Formal Claim

```CFEL
# model
$relation[<Relation>, (.Name = IS_VALUE_CONSTRAINT_OF)];

$inverse[<Relation>, (.Name = HAS_VALUE_CONSTRAINT)];

$relation <((HAS_INVERSE)) $inverse;

$relation ((HAS_CLASSIFICATION)) Derivation == Derived;

$host ((IS_VALUE_CONSTRAINT_OF)) $target
```

### Prose Claim

The Host is constraint data and the Target is the qualified model Subject or instance. This is the inverse view of HAS_VALUE_CONSTRAINT.

## Semantics

IS_VALUE_CONSTRAINT_OF expresses the derived inverse view.
