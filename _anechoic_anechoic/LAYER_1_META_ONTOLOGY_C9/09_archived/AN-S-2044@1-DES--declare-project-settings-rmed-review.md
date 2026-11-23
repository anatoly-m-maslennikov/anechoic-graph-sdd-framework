---
atom_family: SPEC
atom_id: AN-S-2044
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 08:06:47 +0400
---

## Summary

Declare Project.Settings.RMED Review

## Claim

### Formal Claim

```CFEL
# model
Project.Settings.RMED Review{::0..1}:: []{::0};

Project.Settings.RMED Review.*[in (Context Headroom Fraction, Max Atoms)]{::0..2}
```

