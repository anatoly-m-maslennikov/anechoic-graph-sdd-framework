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
  version: 27
  updated_at: '2026-11-11T19:34:00+04:00'
---
## Summary

Place Carriers by Applicable Status Delivery

## Claim

### Prose Claim

Resolve the Current Atom's base directory from its logical Container.

- Scope Unit Container. Use the Atom's Role folder in that Scope Unit.
- Atom Container. Use the containing Atom's matching directory.

Place Active Atoms directly in the base directory. Place other Current Atoms in the derived Status folder within that base.

For other Artifacts, use the most specific applicable Delivery rule. Where a qualified Artifact Status model exists and no specific mapping applies, Active uses the canonical Current directory and another Status uses its lowercase Status subfolder. Where there is no qualified Status model, derive placement from the Artifact's Delivery rule.

### Formal Claim

```CFEL
# model
Atom/(.Header.State.Status >| Status Group = Current).Header.Destination.File.Path == PATH_TEMPLATE("<container>/<status folder>");
Atom/(.Header.State.Status := Active).Header.Destination.File.Path == PATH_TEMPLATE("<container>");
```
