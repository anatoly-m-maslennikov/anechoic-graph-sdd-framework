---
atom_family: SPEC
atom_id: AN-S-2227
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T22:57:02.382288+00:00"
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
