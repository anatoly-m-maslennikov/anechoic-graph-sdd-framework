---
atom_family: SPEC
atom_id: AN-S-2241
container:
  component: C43
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 6
  updated_at: '2026-11-12T16:59:43.837031+00:00'
---
## Summary

Verify Workbench full reread

## Claim

### Prose Claim

Verify full reread recreates derived state from governed sources through the same MCP/health operation, preserving sources/saved items/Journal and failing explicitly without retry for invalid required source/startup. Recreate the SQL tables and derived state under the installed schema and relation registry. Rebuilt rows, relations and graph omit stale data and old result IDs. The explicitly loaded Archive Scope Unit and Role pairs remain loaded and queryable before reread reports ready. Archive sources outside those pairs remain unloaded. Saved query/View remain. `workbench_reread` is Service discovery without generic registry. Invalid Declaration leaves not-ready with no fallback; invalid ordinary source uses reader behavior rather than stale state; MCP remains usable.
