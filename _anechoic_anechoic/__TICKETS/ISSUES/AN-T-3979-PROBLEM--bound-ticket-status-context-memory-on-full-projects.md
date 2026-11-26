---
atom_family: TKT
atom_id: AN-T-3979
concern:
- subject: C68
  path: Project Structure.components
  relation: affects
container:
  component: C68
priority: 2
context:
  template: problem
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-26T05:13:50.810810Z'
---
## Summary

Bound Ticket status context memory on full Projects

## Claim

### Prose Claim

On 0.4.4.76, production MCP refused the status change for AN-T-3971@1 with projection_refresh_failed and no effects. The lifecycle context query failed to allocate 32.0 MiB with 215.8 MiB already in use under the 256 MB DuckDB limit. Studio remained ready and served reads.

## Resolution criteria

Change the status of one Ticket on the full Project within the query memory budget. Verify the new status through MCP.

[AN-T-3968](../TASKS/done/AN-T-3968-EPIC--merge-the-meta-ontology-and-spec-engine-into-amm-dev.md)
