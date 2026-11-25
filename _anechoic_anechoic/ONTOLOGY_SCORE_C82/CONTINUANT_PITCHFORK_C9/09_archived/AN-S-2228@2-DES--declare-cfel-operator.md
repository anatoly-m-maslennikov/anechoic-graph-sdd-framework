---
atom_family: SPEC
atom_id: AN-S-2228
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 20:33:16 +0400
---

## Summary

Declare CFEL operator ?==

## Claim

### Formal Claim

```CFEL
# model
Operator//Fallback == "?=="
```

## Semantics

Conditionally assign the first available valid value to a missing Object Property in the Model. This does not itself write a Carrier; persistence is the responsibility of an adapter or Delivery rule.
