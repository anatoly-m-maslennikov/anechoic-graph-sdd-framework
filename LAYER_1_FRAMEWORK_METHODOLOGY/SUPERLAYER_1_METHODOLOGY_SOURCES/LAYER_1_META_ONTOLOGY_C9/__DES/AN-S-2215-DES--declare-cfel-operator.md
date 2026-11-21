---
atom_family: SPEC
atom_id: AN-S-2215
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T05:28:45.975735+00:00'
---

## Summary

Declare CFEL operator ()

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//Grouping', value='"()"')
```

## Semantics

Group one CFEL expression; parentheses do not create a Node or Relation. When AND and OR occur in one Boolean expression, use parentheses to make their grouping explicit; neither has implicit precedence over the other.
