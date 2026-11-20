---
atom_family: SPEC
atom_id: AN-S-2214
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T05:28:42.754720+00:00'
---

## Summary

Declare CFEL operator >

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//GreaterThan', value='">"')
```

## Semantics

Test that the left numeric value is greater than the right numeric value.
