---
atom_family: TKT
atom_id: AN-T-4035
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T01:15:48.607977+00:00"
---
## Summary

Load built Model assets before Project Spec ingestion

## Acceptance

Admit the Project Model from .anechoic_runtime/assets. Report a failed admission and load the Model bundled in the image. Keep Project-specific Structure bound to its Project and Model.

## Evidence

C71 tests admitted a bound asset, rejected unusable assets with a reason,
and replaced a refused asset after bootstrap. The checkout MCP read used
the bundled Model when no admitted Project asset was available.
See `an-t-3476-asset-and-snapshot.xml` and
`an-t-3476-mcp-local-checkout.log` in the session evidence.
