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
  version: 32
  updated_at: '2026-11-11T18:45:40+04:00'
---
## Summary

Materialize Content Role Directories on First Artifact

## Claim

### Prose Claim

Within a Scope Unit, derive the Atom's Role folder from `Header.Context.Role`. Create the folder when the first Atom needs it. Role folders organize files within their Scope Unit.

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
