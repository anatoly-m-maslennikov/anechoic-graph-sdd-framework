---
atom_family: SPEC
atom_id: AN-S-2066
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

Declare Atom.Header.Ref ID

## Claim

### Prose Claim

For a Current Atom, Ref ID is its base Atom ID. For an Archived Atom, Ref ID is `<ID>@<Version>`. For a Draft Atom, Ref ID is `<ID>@<Version>-draft`.

### Formal Claim

```CFEL
# model
Atom.Header.Identity.Ref ID{::1} :: [string]{::1};

Atom.Header.Identity.Ref ID.*[]{::0}
```
