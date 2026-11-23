---
atom_family: SPEC
atom_id: AN-S-2046
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

Declare Project.Settings.Authority Modes.Project Authority Mode

## Claim

### Prose Claim


The permitted values are `strict` and `casual`. The effective selection follows the applicable authority-mode resolution.

### Formal Claim

```CFEL
# model
Project.Settings.Authority Modes.Project Authority Mode{::1}:: {::1};

Project.Settings.Authority Modes.Project Authority Mode.*[]{::0}
```

