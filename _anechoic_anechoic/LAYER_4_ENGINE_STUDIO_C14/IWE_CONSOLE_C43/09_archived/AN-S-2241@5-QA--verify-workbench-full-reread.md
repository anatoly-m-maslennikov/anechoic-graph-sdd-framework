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
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify Workbench full reread

## Claim

### Prose Claim

Verify full reread recreates derived state from governed sources through the same MCP/health operation, preserving sources/saved items/Journal and failing explicitly without retry for invalid required source/startup. A declared-property change rebuilds database/WAL/temp/schema and rereads source; rebuilt rows/relations/graph/results lack stale state and old result IDs. Saved query/View remain. `workbench_reread` is Service discovery without generic registry. Invalid Declaration leaves not-ready with no fallback; invalid ordinary source uses reader behavior rather than stale state; MCP remains usable.
