---
atom_family: SPEC
atom_id: AN-S-2212
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-13T05:28:34.204151+00:00'
---

## Summary

Declare CFEL operator ;

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//ExpressionSeparator', value='";"')
```

## Semantics

Separate complete CFEL expressions with `;`; a line break is layout only. Read contiguous `<;` and `;>` as Property-order tokens, not as the standalone separator.
