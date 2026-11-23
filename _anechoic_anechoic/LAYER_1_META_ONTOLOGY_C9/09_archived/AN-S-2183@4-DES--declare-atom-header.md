---
atom_family: SPEC
atom_id: AN-S-2183
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-11 16:27:40 +0400
---
## Summary

Declare Atom.Header

## Claim

### Prose Claim

Atom.Header groups the Atom Properties carried in YAML frontmatter, including for Draft Atoms.

### Formal Claim

```CFEL
# model
Atom.Header{::1} :: []{::0};

Atom.Header.*[string, in (Identity, Context, Relations, State, Destination)]{::0+};

Atom.Header.Identity ;> Atom.Header.Context;

Atom.Header.Context ;> Atom.Header.Relations;

Atom.Header.Relations ;> Atom.Header.State;

Atom.Header.State ;> Atom.Header.Destination
```

