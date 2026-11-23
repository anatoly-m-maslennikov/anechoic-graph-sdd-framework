---
atom_family: SPEC
atom_id: AN-S-2219
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T05:29:06.261160+00:00'
---

## Summary

Declare CFEL operator <=

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//LessOrEqual', value='"<="')
```

## Semantics

Test that the left numeric value is less than or equal to the right numeric value.
