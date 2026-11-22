---
atom_family: SPEC
atom_id: AN-S-2230
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-13T05:29:54.280355+00:00'
---
## Summary

Declare CFEL operator OR

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Disjunction', value='"OR"')
```

## Semantics

At least one Boolean operand must be true. Parenthesize mixed AND/OR expressions to make grouping explicit.
