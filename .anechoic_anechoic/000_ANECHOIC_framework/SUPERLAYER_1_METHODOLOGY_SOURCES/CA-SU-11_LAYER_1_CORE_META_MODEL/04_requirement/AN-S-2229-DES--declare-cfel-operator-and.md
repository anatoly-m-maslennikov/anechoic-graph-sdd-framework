---
identity:
  atom_id: AN-S-2229
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-13T05:29:51.943464+00:00'
---
## Summary

Declare CFEL operator AND

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Conjunction', value='"AND"')
```

## Semantics

Both Boolean operands must be true. Parenthesize mixed AND/OR expressions to make grouping explicit.
