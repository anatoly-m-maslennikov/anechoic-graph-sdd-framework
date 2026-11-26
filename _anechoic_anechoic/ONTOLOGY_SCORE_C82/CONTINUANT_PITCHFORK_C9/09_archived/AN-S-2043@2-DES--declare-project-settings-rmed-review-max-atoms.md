---
atom_family: SPEC
atom_id: AN-S-2043
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

Declare Project.Settings.RMED Review.Max Atoms

## Claim

### Prose Claim


When present, the value is positive. Its absence supplies no default.

### Formal Claim

```CFEL
# model
Project.Settings.RMED Review.Max Atoms:: [int]{::0..1};

Project.Settings.RMED Review.Max Atoms.*[]{::0}
```

