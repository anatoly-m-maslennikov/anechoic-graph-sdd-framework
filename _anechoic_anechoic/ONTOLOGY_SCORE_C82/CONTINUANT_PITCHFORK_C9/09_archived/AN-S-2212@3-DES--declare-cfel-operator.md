---
atom_family: SPEC
atom_id: AN-S-2212
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:56:59.106756+00:00"
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
