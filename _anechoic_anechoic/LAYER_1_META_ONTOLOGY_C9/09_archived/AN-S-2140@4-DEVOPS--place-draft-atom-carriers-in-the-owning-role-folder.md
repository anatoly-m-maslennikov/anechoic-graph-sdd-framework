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
  version: 4
  updated_at: '2026-11-11T19:34:00+04:00'
---

## Summary

Place Draft Atom Carriers in the owning Role folder

## Claim

### Prose Claim

Place Draft Atom Markdown Carriers in the shared `<owning scope unit>/<role folder>/<status folder>/` directory. The Atom's owning Scope Unit and Role determine this directory.

### Formal Claim

```CFEL
# model
Atom/(.Header.State.Status := Draft).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/<role folder>/<status folder>");
```
