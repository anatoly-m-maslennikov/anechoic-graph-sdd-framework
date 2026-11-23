---
atom_family: SPEC
atom_id: AN-S-2068
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-11T18:17:52+04:00'
---

## Summary

Declare File Layout Form

## Claim

### Prose Claim

A File Layout Claim specifies how delivered files are named, where they are placed, or how files and folders are arranged. Paths are relative to the repository root.

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Delivery)).Header.Context.Form :: File Layout;
```
