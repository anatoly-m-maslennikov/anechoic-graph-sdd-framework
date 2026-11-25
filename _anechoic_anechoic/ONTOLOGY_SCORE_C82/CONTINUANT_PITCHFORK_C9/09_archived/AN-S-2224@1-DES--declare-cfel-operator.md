---
atom_family: SPEC
atom_id: AN-S-2224
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

Declare CFEL operator **

## Claim

### Formal Claim

```CFEL
# model
Operator//RecursiveWildcard == "**"
```

## Semantics

Select distinct dependent Property identities recursively below p in one bearer.
A `p.**` count aggregates that selection across all descendant depths; it does
not count values or another bearer's selection.
