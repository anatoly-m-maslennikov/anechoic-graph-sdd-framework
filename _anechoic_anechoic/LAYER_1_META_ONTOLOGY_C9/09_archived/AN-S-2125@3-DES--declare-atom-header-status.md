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
  version: 3
  updated_at: '2026-11-11T19:34:00+04:00'
---
## Summary

Declare Atom.Header.Status

## Claim

### Prose Claim

A Status with a dedicated folder has one integer Status Order Number from 0 through 999. Order numbers are distinct across Status values. Declare each number once, including for a Status admitted by several Roles. Active uses its Container's base directory.

### Formal Claim

```CFEL
# model
Atom.Header.State.Status{::1}:: [string]{::1};

Atom.Header.State.Status.*[]{::0};

Atom.Header.State.Status :: Draft;

Atom.Header.State.Status :: Active;

Atom.Header.State.Status :: Archived;

Atom/(.Header.State.Status := Draft).Header.State.Status >| (Status Order Number == 0);

Atom/(.Header.State.Status := Archived).Header.State.Status >| (Status Order Number == 99);
```
