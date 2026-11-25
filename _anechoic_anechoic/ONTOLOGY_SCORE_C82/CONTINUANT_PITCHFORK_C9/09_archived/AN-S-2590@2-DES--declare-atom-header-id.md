---
atom_family: SPEC
atom_id: AN-S-2590
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-11T18:31:44+04:00'
---
## Summary

Declare Atom.Header.ID

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Identity.ID{::1}:: [string]{::1};

Atom.Header.Identity.ID.*[]{::0};

# instances
Atom//$atom;

IF (($atom.Header.State.Status >| Status Group = Current) OR ($atom.Header.State.Status >| Status Group = Backlog) OR ($atom.Header.State.Status >| Status Group = Archived))
THEN (IMMUTABLE($atom.Header.Identity.ID))
```
