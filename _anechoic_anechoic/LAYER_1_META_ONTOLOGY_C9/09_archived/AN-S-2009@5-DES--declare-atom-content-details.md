---
atom_family: SPEC
atom_id: AN-S-2009
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Declare Atom.Content.Details

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in RMED).Content.Details:: {::0..1};

Atom/(.Header.Context.Role in RMED).Content.Details.*[string]{::0+}
```

