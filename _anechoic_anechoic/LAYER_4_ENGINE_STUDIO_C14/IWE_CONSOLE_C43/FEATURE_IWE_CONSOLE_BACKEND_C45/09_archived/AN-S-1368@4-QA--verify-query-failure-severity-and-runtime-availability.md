---
atom_family: SPEC
atom_id: AN-S-1368
container:
  component: C45
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify query-failure severity and runtime availability.

## Claim

### Prose Claim

Invalid SQL or query arguments return useful request error, `query_error` at WARNING and `outcome: failed`, while the healthy owner remains usable. Workbench-unavailable or unexpected runtime failure remains ERROR with `outcome: blocked` and its restart/runtime boundary. Verify a valid native MCP/HTTP request succeeds after an invalid one.
