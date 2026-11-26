---
atom_family: SPEC
atom_id: AN-S-2010
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: '2026-11-11T18:56:17+04:00'
---
## Summary

Declare Atom/(.Role := Concern)

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Role :: Concern;

Atom/(.Header.Context.Role := Concern) >| (Role Order Number == 1);
```

## Semantics

A Concern identifies a question, conflict, or problem.
