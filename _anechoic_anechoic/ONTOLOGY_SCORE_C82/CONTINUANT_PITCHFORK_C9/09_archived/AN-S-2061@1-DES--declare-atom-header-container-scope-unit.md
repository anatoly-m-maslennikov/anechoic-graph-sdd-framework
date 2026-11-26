---
atom_family: SPEC
atom_id: AN-S-2061
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 22:47:24 +0400
---

## Summary

Declare Atom.Header.Container.scope_unit

## Claim

### Prose Claim

The value is the stable ID of the containing Scope Unit.
### Formal Claim

```CFEL
# model
Atom.Header.Context.Container.scope_unit :: [string]{::0..1};

Atom.Header.Context.Container.scope_unit.*[]{::0}
```

