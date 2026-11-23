---
atom_family: SPEC
atom_id: AN-S-2216
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T05:28:49.418850+00:00'
---

## Summary

Declare CFEL operator *

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//ImmediateWildcard', value='"*"')
```

## Semantics

Select immediate dependent Properties in `p.*`.
