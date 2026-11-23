---
atom_family: SPEC
atom_id: AN-S-2055
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Declare Atom.Header.Carrier Destination.File

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Destination.File{::1}:: []{::0};

Atom.Header.Destination.File.*[in (Name, Path)]{::2};

Atom.Header.Destination.File.*:: [string]
```
