---
atom_family: SPEC
atom_id: AN-S-2137
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 26
  updated_at: '2026-11-11T19:06:04+04:00'
---
## Summary

Place Carriers by Applicable Status Delivery

## Claim

### Prose Claim

Resolve the Current Atom's base directory from its logical Container.

- Scope Unit Container. Use the Atom's Role folder in that Scope Unit.
- Atom Container. Use the containing Atom's matching directory.

Place Active Atoms directly in the base directory. Place Done and Resolved Atoms in `020_done/` and `021_resolved/`. Place Canceled Atoms in `040_canceled/`.

For other Artifacts, use the most specific applicable Delivery rule. Where a qualified Artifact Status model exists and no specific mapping applies, Active uses the canonical Current directory and another Status uses its lowercase Status subfolder. Where there is no qualified Status model, derive placement from the Artifact's Delivery rule.

### Formal Claim

```CFEL
# model
Atom/(.Header.State.Status := Active).Header.Destination.File.Path == PATH_TEMPLATE("<container>");
Atom/(.Header.State.Status := Done).Header.Destination.File.Path == PATH_TEMPLATE("<container>/020_done");
Atom/(.Header.State.Status := Resolved).Header.Destination.File.Path == PATH_TEMPLATE("<container>/021_resolved");
Atom/(.Header.State.Status := Canceled).Header.Destination.File.Path == PATH_TEMPLATE("<container>/040_canceled");
```
