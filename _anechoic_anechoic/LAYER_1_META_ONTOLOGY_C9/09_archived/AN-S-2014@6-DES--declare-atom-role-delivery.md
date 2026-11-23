---
atom_family: SPEC
atom_id: AN-S-2014
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

Declare Atom/(.Role := Delivery)

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Role :: Delivery;

Atom/(.Header.Context.Role := Delivery) >| (Role Order Number == 7);
```

## Semantics

A Delivery specifies how results are represented, packaged, stored and made available through their Carriers at their intended destinations.
