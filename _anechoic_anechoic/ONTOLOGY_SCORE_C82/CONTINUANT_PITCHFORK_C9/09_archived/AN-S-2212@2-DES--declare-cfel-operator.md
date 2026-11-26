---
atom_family: SPEC
atom_id: AN-S-2212
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-05 22:47:24 +0400
---

## Summary

Declare CFEL operator ;

## Claim

### Formal Claim

```CFEL
# model
Operator//ExpressionSeparator == ";"
```

## Semantics

Separate complete CFEL expressions with `;`; a line break is layout only. Read contiguous `<;` and `;>` as Property-order tokens, not as the standalone separator.
