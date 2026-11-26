---
atom_family: SPEC
atom_id: AN-S-2227
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 08:06:47 +0400
---

## Summary

Declare CFEL operator :=

## Claim

### Formal Claim

```CFEL
# model
Operator//SubjectValueSelection == ":="
```

## Semantics

In a Subject or a filtered Node expression in a Formal Claim, combine an admitted Property value with selection; for example, `Workflow/(.Purpose := Runtime)`. It is not assignment.
