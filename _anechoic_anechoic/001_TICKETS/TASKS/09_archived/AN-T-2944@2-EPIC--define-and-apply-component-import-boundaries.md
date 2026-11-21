---
atom_family: TKT
atom_id: AN-T-2944
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: archived
  version: 2
  updated_at: '2026-11-21T18:31:22.080061+00:00'
---

## Summary

Define and apply Component import boundaries

## Objective

Give each current Component an authored Contract and declare the Code Access that its Realization needs.

## Work

1. Declare Code Access in Component Manifests.
2. Give each code-bearing Package a `__family_pub` entry Module for its parent and siblings. Prefer one such entry Module and add an optional `__pub` entry Module. Keep implementation Modules unmarked and Package-local. Apply the rule separately to each Package.
3. Write each Component Contract and implement its code interface.
4. Bind exact Contract revisions to their Realization Packages.
5. Resolve forbidden imports after Tasks 1–4 pass. Use Component Seed as the name for a Package with its own Spec that may later become a Component.
