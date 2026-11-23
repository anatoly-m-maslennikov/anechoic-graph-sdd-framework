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
  version: 2
  updated_at: 2026-11-05 14:23:38 +0400
---

## Summary

Expose every Workbench backend capability through MCP

## Claim scope

Workbench backend capabilities exposed through MCP.

## Claim

Expose every Workbench backend capability through MCP with the same arguments, results, errors and saved URLs as the web interface. Include `query_run(save=true)`, `query_page`, `query_check`, `query_schema`, `view_save`, `query_load` and `query_saved_list`. There is no separate `query_save` or `worksheet_save` capability. Browser-only preferences and local draft state are not backend capabilities and are not exposed through MCP.

The first WORKBENCH_CODEX conversation-control transport is an exception. Its open or resume, message and event stream, interaction or approval reply, and interrupt operations are UI-only. The underlying actions called through the conversation remain MCP capabilities. This exception applies only to conversation control and does not change the rule for other Workbench backend capabilities.
