---
atom_family: SPEC
atom_id: AN-S-2012
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

Declare Atom/(.Role := Method)

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Role :: Method;

Atom/(.Header.Context.Role := Method) >| (Role Order Number == 5);
```

## Semantics

A Method specifies domain and engineering designs, mechanisms or working approaches for achieving required results.
