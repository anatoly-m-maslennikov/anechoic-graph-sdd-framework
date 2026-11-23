---
atom_family: SPEC
atom_id: AN-S-4347
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

Declare Scope Unit Path

## Claim

### Prose Claim


The Path lists Scope Unit identities along the complete declared containment chain from the root to the addressed Scope Unit.

### Formal Claim

```CFEL
# model
Scope Unit.Path{::1}:: [string]{::1+};

Scope Unit.Path.*[]{::0}
```

