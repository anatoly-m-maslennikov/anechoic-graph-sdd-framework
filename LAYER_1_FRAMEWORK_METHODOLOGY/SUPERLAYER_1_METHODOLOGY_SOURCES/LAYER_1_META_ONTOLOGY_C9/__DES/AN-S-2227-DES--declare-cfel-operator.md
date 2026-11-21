---
atom_family: SPEC
atom_id: AN-S-2227
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T05:29:42.684007+00:00'
---

## Summary

Declare CFEL operator :=

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//SubjectValueSelection', value='":="')
```

## Semantics

In a Subject or a filtered Node expression in a Formal Claim, combine an admitted Property value with selection; for example, `Workflow/(.Purpose := Runtime)`. It is not assignment.
