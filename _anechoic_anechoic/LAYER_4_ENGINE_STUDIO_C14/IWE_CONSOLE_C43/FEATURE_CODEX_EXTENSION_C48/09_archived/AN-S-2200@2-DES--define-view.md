---
atom_family: SPEC
atom_id: AN-S-2200
container:
  component: C48
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-05 16:45:35 +0400
---

## Summary

Define View

## Claim

### Prose Claim

A View is a Workbench SQL document in one Workspace. It has one stable string ID, one SQL script and may have one name. A View can be edited, run, fetched, focused, renamed, removed or saved through the Workspace operations.
### Formal Claim

```CFEL
Workspace >{1+} View;
View.id [string]{1};
View.sql [string]{1};
View.name [string]{0..1}
```

