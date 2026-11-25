---
atom_family: SPEC
atom_id: AN-S-2221
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T05:29:16.220257+00:00'
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
