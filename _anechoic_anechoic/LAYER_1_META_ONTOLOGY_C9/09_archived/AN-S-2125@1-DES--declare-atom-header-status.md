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
  version: 1
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Declare Atom.Header.Status

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Status{::1}:: [string]{::1};

Atom.Header.Status.*[]{::0};

Atom.Header.Status: Draft;

Atom.Header.Status: Active;

Atom.Header.Status: Archived
```
