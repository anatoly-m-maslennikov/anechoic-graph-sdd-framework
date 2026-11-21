---
atom_family: SPEC
atom_id: AN-S-2870
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

Declare IS_ALLOWED_VALUE_OF

## Claim

### Formal Claim

```CFEL
# model
$relation[<Relation>, (.Name = IS_ALLOWED_VALUE_OF)];

$inverse[<Relation>, (.Name = HAS_ALLOWED_VALUE)];

$relation <((HAS_INVERSE)) $inverse;

$relation ((HAS_CLASSIFICATION)) Derivation == Derived;

$host ((IS_ALLOWED_VALUE_OF)) $target
```

### Prose Claim

The Host is an admitted literal value or literal-alternative set and the Target is the qualified model Subject or instance. This is the inverse view of HAS_ALLOWED_VALUE.

## Semantics

IS_ALLOWED_VALUE_OF expresses the derived inverse view.
