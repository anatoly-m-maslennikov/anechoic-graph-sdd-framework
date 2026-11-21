---
atom_family: SPEC
atom_id: AN-S-2871
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

Declare HAS_VALUE_CONSTRAINT

## Claim

### Formal Claim

```CFEL
# model
$relation[<Relation>, (.Name = HAS_VALUE_CONSTRAINT)];

$inverse[<Relation>, (.Name = IS_VALUE_CONSTRAINT_OF)];

$relation ((HAS_INVERSE)) $inverse;

$relation ((HAS_CLASSIFICATION)) Derivation == Direct;

alias($relation) == "::";

$host ((HAS_VALUE_CONSTRAINT)) $target
```

### Prose Claim

The Host is the qualified model Subject or instance to which the constraint applies. The Target is constraint data, including a Format or cardinality constraint, not a model Node. For the same qualified Subject, all applicable HAS_VALUE_CONSTRAINT expressions, including inherited expressions, combine by AND. If none applies, that group contributes true. Final admissibility combines this AND group with the applicable HAS_ALLOWED_VALUE OR group. `x :: [string]` and `x :: {::1}` may be written together as `x :: [string]{::1}`.

## Semantics

HAS_VALUE_CONSTRAINT expresses the direct value rule.
