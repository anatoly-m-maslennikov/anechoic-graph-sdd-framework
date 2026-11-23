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
  version: 31
  updated_at: '2026-11-11T17:52:20+04:00'
---
## Summary

Materialize Content Role Directories on First Artifact

## Claim

### Prose Claim


administrative Content Role directories in Scope Units.


a Scope Unit's administrative Content Role directory **must** be materialized for canonical Artifact placement **only** **when** the first current Artifact requires that placement.

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role := Concern).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/01_concern/<placement>");
Atom/(.Header.Context.Role := Analysis and Advisory).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/02_analysis/<placement>");
Atom/(.Header.Context.Role := Plan).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/03_plan/<placement>");
Atom/(.Header.Context.Role := Requirement).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/04_requirement/<placement>");
Atom/(.Header.Context.Role := Method).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/05_method/<placement>");
Atom/(.Header.Context.Role := Evaluation).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/06_evaluation/<placement>");
Atom/(.Header.Context.Role := Delivery).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/07_delivery/<placement>");
Atom/(.Header.Context.Role := Operations).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/09_operations/<placement>");
```

## Details

an absent Content Role directory **must** represent empty role placement, **not** an absent Scope Unit. this administrative directory does **not** itself carry a Structural Entity **or** become a Directory Carrier under CA-D-451. this materialization condition does **not** require deletion of an existing empty directory.
