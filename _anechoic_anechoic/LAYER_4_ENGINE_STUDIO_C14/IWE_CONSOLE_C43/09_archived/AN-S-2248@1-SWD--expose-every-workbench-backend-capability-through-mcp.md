---
atom_family: SPEC
atom_id: AN-S-2248
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-04 23:19:17 +0400
---

## Summary

Expose every Workbench backend capability through MCP

## Claim scope

Workbench backend capabilities exposed through MCP.

## Claim

Expose every Workbench backend capability through MCP with the same arguments, results, errors and saved URLs as the web interface. Include `query_run`, `query_page`, `query_check`, `query_schema`, `query_save`, `worksheet_save`, `query_load` and `query_saved_list`. Browser-only preferences and local draft state are not backend capabilities and are not exposed through MCP.
