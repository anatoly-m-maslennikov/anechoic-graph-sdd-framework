---
atom_family: SPEC
atom_id: AN-S-1679
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 13
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Enable containment for Workflow Atoms

## Claim

### Prose Claim


Containment capability of Workflow Atoms.


`Atom/(.Header.Role := Operations)/(.Header.Form := Workflow).Enabled Relations.Contains` **must** be True. a Workflow Atom **may** contain Step Atoms.

## Details

The Workflow remains an Atom. Its Steps retain their own definitions and Action references. This permission does not copy shared Actions into a Workflow or replace its declared control flow with folder order.
