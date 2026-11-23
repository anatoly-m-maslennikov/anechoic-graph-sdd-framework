---
atom_family: SPEC
atom_id: AN-S-4230
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---

## Summary

Declare Substep

## Claim

```CFEL
Atom/(.Role: Operations)/Substep;
Substep//{:1}((IS_CONTAINED_BY)) Step//;
Substep//{:1}((RUN)) Action//
```

## Semantics

A Substep is a leaf unit within a Step. It runs a reusable Action.
