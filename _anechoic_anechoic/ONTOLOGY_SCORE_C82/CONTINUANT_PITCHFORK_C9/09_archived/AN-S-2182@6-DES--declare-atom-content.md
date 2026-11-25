---
atom_family: SPEC
atom_id: AN-S-2182
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-11-05 22:47:24 +0400
---
## Summary

Declare Atom.Content

## Claim

### Formal Claim

```CFEL
# model
Atom.Content{::1}:: []{::0};

Atom.Content.*[string]{::0+};

Atom.Content.**[string]{::0+};

Atom.Content.**:: [markdown];

Atom/(.Header.Context.Role in RMED).Content.Summary ;> Atom/(.Header.Context.Role in RMED).Content.Claim;

Atom/(.Header.Context.Role in RMED).Content.Claim ;> Atom/(.Header.Context.Role in RMED).Content.Semantics;

Atom/(.Header.Context.Role in RMED).Content.Semantics ;> Atom/(.Header.Context.Role in RMED).Content.Details
```

