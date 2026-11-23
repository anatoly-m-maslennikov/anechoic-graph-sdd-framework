---
atom_family: SPEC
atom_id: AN-S-2051
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

Declare Atom.Header.Version

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.State.Version{::1}:: [int]{::1};

Atom.Header.State.Version.*[]{::0};

Atom.Header.State.Version >= 1
```
