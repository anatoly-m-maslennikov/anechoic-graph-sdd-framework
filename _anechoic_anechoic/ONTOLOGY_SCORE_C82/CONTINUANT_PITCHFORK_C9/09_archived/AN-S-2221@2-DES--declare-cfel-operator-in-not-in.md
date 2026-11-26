---
atom_family: SPEC
atom_id: AN-S-2221
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T22:57:00.922616+00:00"
---

## Summary

Declare CFEL operator in / not in

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Membership', value='"in / not in"')
```

## Semantics

Test membership or non-membership in a selected set.
