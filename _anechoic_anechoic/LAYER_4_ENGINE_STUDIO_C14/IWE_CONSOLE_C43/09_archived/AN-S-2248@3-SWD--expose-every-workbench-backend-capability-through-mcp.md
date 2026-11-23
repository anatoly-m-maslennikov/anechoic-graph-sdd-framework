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
  version: 3
  updated_at: 2026-11-05 16:45:35 +0400
---

## Summary

Expose every Workbench backend capability through MCP

## Claim scope

Workbench backend capabilities exposed through MCP.

## Claim

Expose every Workbench backend capability through MCP with the same arguments, results, errors and saved URLs as the web interface. Include `query_run(save=true)`, `query_page`, `query_check`, `query_schema`, `view_save`, `query_load` and `query_saved_list`. There is no separate `query_save` or `worksheet_save` capability. Browser-only preferences and local draft state are not backend capabilities and are not exposed through MCP.

Workspace and View coordination is a backend capability and is exposed through MCP with the same state as the embedded interface. Native Codex chat is outside Workbench; Workbench does not duplicate its conversation control.
