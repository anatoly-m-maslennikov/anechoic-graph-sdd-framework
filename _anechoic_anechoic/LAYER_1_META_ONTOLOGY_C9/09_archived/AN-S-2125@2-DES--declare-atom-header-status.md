---
atom_family: SPEC
atom_id: AN-S-2125
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-11 13:45:22 +0400
---
## Summary

Declare Atom.Header.Status

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.State.Status{::1}:: [string]{::1};

Atom.Header.State.Status.*[]{::0};

Atom.Header.State.Status :: Draft;

Atom.Header.State.Status :: Active;

Atom.Header.State.Status :: Archived
```
