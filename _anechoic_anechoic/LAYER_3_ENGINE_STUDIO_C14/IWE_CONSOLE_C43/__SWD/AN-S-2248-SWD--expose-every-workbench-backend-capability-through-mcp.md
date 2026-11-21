---
atom_family: SPEC
atom_id: AN-S-2248
structure:
  container:
    component: C43
  tier: 4
context:
  lens: SWD
state:
  status: active
  version: 8
  updated_at: '2026-11-13T15:52:26.342118+00:00'
---

## Summary

Expose every Workbench backend capability through MCP

## Claim scope

Workbench backend capabilities exposed through MCP.

## Claim

### Prose Claim

Implement each Workbench backend capability once in the shared backend. Expose it through web and MCP adapters with the same arguments, results, errors and saved URLs. Include `query_run(save=true)`, `query_page`, `query_check`, `query_schema`, `view_save`, `query_load` and `query_saved_list`. There is no separate `query_save` or `worksheet_save` capability. Browser-only preferences and local draft state are not backend capabilities and are not exposed through MCP.

Workspace and View coordination is a backend capability and is exposed through MCP with the same state as the embedded interface. Native Codex chat is outside Workbench; Workbench does not duplicate its conversation control.

Result-file export is a shared backend capability available through both interfaces. Use the same explicit `result_delivery` and `result_format` arguments. File delivery is the default; browser grids request inline pages. Omit automatic SQL echoes from execution, validation and result fetch. Explicit SQL reads remain available.
