---
atom_family: SPEC
atom_id: AN-S-2200
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Define View

## Claim

### Prose Claim

A View is a Workbench SQL document in one Workspace. It has one stable string ID, one complete SQL query and may have one name. A View can be edited, run, fetched, focused, renamed, removed or saved through the Workspace operations.
### Formal Claim

```CFEL
# model
View.id{::1}:: [string]{::1};
View.sql{::1}:: [string]{::1};
View.name{::0..1}:: [string]{::0..1}
```

