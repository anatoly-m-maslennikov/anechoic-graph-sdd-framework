---
atom_family: SPEC
atom_id: AN-S-2013
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: '2026-11-11T18:56:17+04:00'
---

## Summary

Declare Atom/(.Role := Evaluation)

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Role :: Evaluation;

Atom/(.Header.Context.Role := Evaluation) >| (Role Order Number == 6);
```

## Semantics

An Evaluation specifies falsifiable checks and how their evidence is interpreted to determine whether required results are achieved.
