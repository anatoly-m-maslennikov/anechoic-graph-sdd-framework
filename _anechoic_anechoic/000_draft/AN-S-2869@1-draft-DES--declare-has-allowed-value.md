---
atom_family: SPEC
atom_id: AN-S-2869
structure:
  container:
    component: C00
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 16:33:24 +0400
---

## Summary

Declare HAS_ALLOWED_VALUE

## Claim

### Formal Claim

```CFEL
# model
$relation[<Relation>, (.Name = HAS_ALLOWED_VALUE)];

$inverse[<Relation>, (.Name = IS_ALLOWED_VALUE_OF)];

$relation ((HAS_INVERSE)) $inverse;

$relation ((HAS_CLASSIFICATION)) Derivation == Direct;

alias($relation) == ":=";

$host ((HAS_ALLOWED_VALUE)) $target
```

### Prose Claim

The Host is the qualified model Subject or instance to which the allowed-value expression applies. The Target is its admitted literal value or a set of literal alternatives; neither is a model Node. For the same qualified Subject, all applicable HAS_ALLOWED_VALUE expressions, including inherited expressions, combine by OR. If none applies, omit the allowed-value group: it imposes no enumeration restriction. `x := a | b` writes alternatives. In a qualified Subject such as `Atom//(.Role := Method)`, `:=` retains its admitted-value and Subject-selection meaning; OR across applicable values in that qualified scope does not remove the selection condition. The final admissibility condition is the OR of applicable HAS_ALLOWED_VALUE expressions AND the AND of applicable HAS_VALUE_CONSTRAINT expressions.

## Semantics

HAS_ALLOWED_VALUE expresses the direct value rule.
