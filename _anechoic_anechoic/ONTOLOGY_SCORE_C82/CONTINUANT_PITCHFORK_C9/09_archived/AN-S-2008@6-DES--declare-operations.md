---
atom_family: SPEC
atom_id: AN-S-2008
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: '2026-11-11T18:56:17+04:00'
---

## Summary

Declare Operations

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Role :: Operations;

Atom/(.Header.Context.Role := Operations) >| (Role Order Number == 9);
```

## Semantics

An Operations Atom specifies work to perform and how it is coordinated, including its sequence, inputs and outputs.
