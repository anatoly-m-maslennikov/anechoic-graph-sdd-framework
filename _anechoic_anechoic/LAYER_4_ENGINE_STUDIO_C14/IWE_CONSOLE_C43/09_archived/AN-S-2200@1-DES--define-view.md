---
atom_family: SPEC
atom_id: AN-S-2200
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 14:23:38 +0400
---

## Summary

Define View

## Claim

### Formal Claim

```CFEL
Workspace >{1+} View;
View.sql [string]{1};
View.name [string]{0..1}
```

### Prose Claim

A View is a Workbench SQL document in one Workspace. It has one SQL script and may have one name. Saving and loading a View are separate Workbench capabilities.
