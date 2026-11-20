---
atom_family: SPEC
atom_id: AN-S-2211
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T05:28:28.889465+00:00'
---

## Summary

Declare CFEL operator =

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Condition', value='"="')
```

## Semantics

Test equality in a Formal Claim or IF condition; it is not assignment.
