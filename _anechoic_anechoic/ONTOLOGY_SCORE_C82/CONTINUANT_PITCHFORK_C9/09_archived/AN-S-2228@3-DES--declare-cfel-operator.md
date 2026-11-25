---
atom_family: SPEC
atom_id: AN-S-2228
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:57:02.972748+00:00"
---

## Summary

Declare CFEL operator ?==

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Fallback', value='"?=="')
```

## Semantics

Conditionally assign the first available valid value to a missing Object Property in the Model. This does not itself write a Carrier; persistence is the responsibility of an adapter or Delivery rule.
