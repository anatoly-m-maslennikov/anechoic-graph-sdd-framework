---
atom_family: SPEC
atom_id: AN-S-2136
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 30
  updated_at: 2026-11-03 23:25:51 +0400
---
## Summary

Materialize Content Role Directories on First Artifact

## Claim

### Prose Claim


administrative Content Role directories in Scope Units.


a Scope Unit's administrative Content Role directory **must** be materialized for canonical Artifact placement **only** **when** the first current Artifact requires that placement.

## Details

an absent Content Role directory **must** represent empty role placement, **not** an absent Scope Unit. this administrative directory does **not** itself carry a Structural Entity **or** become a Directory Carrier under CA-D-451. this materialization condition does **not** require deletion of an existing empty directory.
