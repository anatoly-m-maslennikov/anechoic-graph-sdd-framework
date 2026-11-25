---
atom_family: SPEC
atom_id: AN-S-1679
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 12
  updated_at: 2026-10-29 07:45:28 +0400
---
## Summary

Enable containment for Workflow Atoms

## Claim scope

Containment capability of Workflow Atoms.

## Claim

`Atom/Content Role: Operations/Type: Workflow.Enabled Relations.Contains` **must** be True. a Workflow Atom **may** contain Step Atoms.

## Details

The Workflow remains an Atom. Its Steps retain their own definitions and Action references. This permission does not copy shared Actions into a Workflow or replace its declared control flow with folder order.
