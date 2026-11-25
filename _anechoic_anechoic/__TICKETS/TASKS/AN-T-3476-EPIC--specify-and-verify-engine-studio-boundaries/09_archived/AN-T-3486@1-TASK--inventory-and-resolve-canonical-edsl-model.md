---
atom_family: TKT
atom_id: AN-T-3486
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T10:24:44.356322+00:00'
---
## Summary

Inventory and resolve canonical eDSL Model

## Work

Inventory the actual eDSL Model declarations and their Node, Property, and Relation bindings. Resolve each to its canonical source and record missing, ambiguous, duplicate, or unsupported bindings. Use explicit Model declarations only; do not infer bindings from Component boundary Manifests or hidden defaults.

## Acceptance

The inventory identifies the real declaration population, canonical resolution for each binding, and every unresolved case. No implicit or guessed binding is admitted.
