---
atom_family: SPEC
atom_id: AN-S-2226
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T05:29:39.474702+00:00'
---

## Summary

Declare CFEL operator !()

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//SelectionExclusion', value='"!()"')
```

## Semantics

Exclude selected branches from a delivery selection.
