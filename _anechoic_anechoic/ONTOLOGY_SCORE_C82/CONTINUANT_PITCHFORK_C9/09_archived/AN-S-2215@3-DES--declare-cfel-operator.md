---
atom_family: SPEC
atom_id: AN-S-2215
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-04 21:11:03 +0400
---

## Summary

Declare CFEL operator ()

## Claim

### Formal Claim

```CFEL
# model
Operator//Grouping == "()"
```

## Semantics

Group one CFEL expression; parentheses do not create a Node or Relation. When AND and OR occur in one Boolean expression, use parentheses to make their grouping explicit; neither has implicit precedence over the other.
