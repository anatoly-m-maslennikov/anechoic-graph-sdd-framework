---
atom_family: SPEC
atom_id: AN-S-2229
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:57:03.771889+00:00"
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
