---
atom_family: SPEC
atom_id: AN-S-4450
container:
  component: C71
tier: 2
context:
  lens: SWD/DBT
state:
  status: active
  version: 1
  updated_at: '2026-11-23T11:51:38.834854+00:00'
---
## Summary

Refresh DuckDB projections by affected key

## Claim

### Prose Claim

Stage each Atom batch once. Use set-based SQL for Atom rows and references, affected graph edges and vertices, and derived metric refresh. Apply old and new keys for moves and deletes in the admission transaction. Keep durable `ops_` facts in base tables. Follow AN-S-3401.
