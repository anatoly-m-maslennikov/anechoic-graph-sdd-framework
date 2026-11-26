---
atom_family: SPEC
atom_id: AN-S-2187
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 19:17:40 +0400
---
## Summary

Declare Scope Unit.order

## Claim

### Formal Claim

```CFEL
# model
Scope Unit.order:: []{::0};

Scope Unit.order.*[in (ordered, number)]{::1..2}
```

## Semantics

order groups the Boolean ordered and the conditional number as sibling Properties. The group has no direct value.
