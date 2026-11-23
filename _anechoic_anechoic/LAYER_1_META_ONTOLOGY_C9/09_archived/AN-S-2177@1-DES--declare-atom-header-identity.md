---
atom_family: SPEC
atom_id: AN-S-2177
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 16:27:40 +0400
---

## Summary

Declare Atom.Header.Identity

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Identity{::1} :: []{::0};

Atom.Header.Identity.*[in (ID, Ref ID)]{::2};

Atom.Header.Identity.ID ;> Atom.Header.Identity.Ref ID
```
