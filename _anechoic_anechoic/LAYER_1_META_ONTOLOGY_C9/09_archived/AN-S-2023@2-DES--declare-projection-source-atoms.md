---
atom_family: SPEC
atom_id: AN-S-2023
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Declare Projection.Source.Atoms

## Claim

### Prose Claim



Each value is an Atom ID with an explicit Version.
### Formal Claim

```CFEL
# model
Projection.Source.Atoms{::0..1}:: [string]{::0+};

Projection.Source.Atoms.*[]{::0}
```

