---
identity:
  atom_id: AN-S-2224
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T05:29:29.795188+00:00'
---

## Summary

Declare CFEL operator **

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//RecursiveWildcard', value='"**"')
```

## Semantics

Select distinct dependent Property identities recursively below p in one bearer.
A `p.**` count aggregates that selection across all descendant depths; it does
not count values or another bearer's selection.
