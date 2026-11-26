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
  version: 3
  updated_at: '2026-11-11T19:06:04+04:00'
---

## Summary

Place Draft Atom Carriers in the owning Role folder

## Claim

### Prose Claim

Place Draft Atom Markdown Carriers in the shared `<owning scope unit>/<role folder>/000_draft/` directory. The Atom's owning Scope Unit and Role determine this directory.

For example, Draft Plans use `<scope unit>/03_plan/000_draft/`.

### Formal Claim

```CFEL
# model
Atom/(.Header.State.Status := Draft).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/<role folder>/000_draft");
```
