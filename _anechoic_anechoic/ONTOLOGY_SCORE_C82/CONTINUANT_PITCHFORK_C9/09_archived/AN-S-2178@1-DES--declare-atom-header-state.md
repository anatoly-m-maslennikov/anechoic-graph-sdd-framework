---
atom_family: SPEC
atom_id: AN-S-2178
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

Declare Atom.Header.State

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.State{::1} :: []{::0};

Atom.Header.State.*[in (Status, Version, Updated At)]{::3};

Atom.Header.State.Status ;> Atom.Header.State.Version;

Atom.Header.State.Version ;> Atom.Header.State.Updated At
```
