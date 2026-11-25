---
atom_family: SPEC
atom_id: AN-S-2140
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: '2026-11-11T17:52:20+04:00'
---

## Summary

Place Draft Atom Carriers in the owning Role folder

## Claim

### Prose Claim

Place Draft Atom Markdown Carriers in the shared `<scope unit>/<role number>_<role name lowercase>/draft/` directory. The Atom's owning Scope Unit and Role determine this directory.

For example, Draft Plans use `<scope unit>/03_plan/draft/`.

### Formal Claim

```CFEL
# model
Atom/(.Header.State.Status := Draft).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/<role folder>/draft");
```
