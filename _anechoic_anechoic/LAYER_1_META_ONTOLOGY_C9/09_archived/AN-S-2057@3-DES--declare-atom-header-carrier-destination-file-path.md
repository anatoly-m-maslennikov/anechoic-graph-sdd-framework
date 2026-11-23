---
atom_family: SPEC
atom_id: AN-S-2057
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Declare Atom.Header.Carrier Destination.File.Path

## Claim

### Prose Claim




Calculated path of the containing directory, relative to the repository root.
### Formal Claim

```CFEL
# model
Atom.Header.Destination.File.Path:: {::1};

Atom.Header.Destination.File.Path.*[]{::0}
```

