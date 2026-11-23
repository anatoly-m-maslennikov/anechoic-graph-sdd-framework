---
atom_family: SPEC
atom_id: AN-S-1357
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---
## Summary

Align MCP Run, Check, and simple web query results

## Claim scope

Direct MCP and web results over one in-memory SQL connector.

## Claim

### Prose Claim

MCP Run, MCP Check, and the web page directly and synchronously invoke one in-memory SQL connector. They add no planner, scheduler, queue, Workflow, or job. Run returns the execution's complete rows, names, types, and counts; Check returns validity and exact counts or the query error. Hashes belong only to source-derived `atoms` and `scope_units` rows: an arbitrary result, including `SELECT COUNT(*)`, gains no hash column.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Multi-row Run through MCP and web | Each direct request returns its own connector result before completion, with exact names, types, rows, and counts. |
| `SELECT COUNT(*) FROM atoms` | Only the requested aggregate column is returned. |
| Invalid SQL or oversized MCP result | The caller receives respectively its query error or explicit full-result delivery failure; no empty success or silent limit occurs. |
| Background source error | The indexer writes stderr and skips the source; the valid direct query result stays ordinary SQL data. |
