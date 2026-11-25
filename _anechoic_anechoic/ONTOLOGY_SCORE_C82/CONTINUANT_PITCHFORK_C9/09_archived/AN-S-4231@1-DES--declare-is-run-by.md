---
atom_family: SPEC
atom_id: AN-S-4231
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 08:06:47 +0400
---

## Summary

Declare IS_RUN_BY

## Claim

An Action is run by a Step or Substep. IS_RUN_BY is the derived inverse of RUN. It expresses the same fact and is not authored separately.

```CFEL
Action// ((IS_RUN_BY)) (in (Step, Substep))//;
((RUN)) ((HAS_INVERSE)) ((IS_RUN_BY));

((IS_RUN_BY)) >| Derivation == Derived;
((IS_RUN_BY)) ((IS_DERIVED_RELATION_OF)) ((RUN))
```

## Semantics


Forward `Host ((IS_RUN_BY)) Target` and reverse `Target <((IS_RUN_BY)) Host` are views of the same Relation fact.
IS_RUN_BY relates Action instance to Step or Substep instance. It is the derived inverse of RUN; it does not add a separately authored fact.

