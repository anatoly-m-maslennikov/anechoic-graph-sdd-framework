---
atom_family: SPEC
atom_id: AN-S-2916
structure:
  container:
    component: C43
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 2
  updated_at: 2026-11-05 16:45:35 +0400
---

## Summary

Provide one Codex conversation per Project

## Claim

### Prose Claim

WORKBENCH_CODEX **must** provide the selected Project's one Workspace with exactly one native persisted Codex conversation. ANECHOIC requests include the explicit `project_root`. A returning browser resumes that Workspace's conversation.

The conversation operates all Tools exposed by enabled MCP servers in the local Codex configuration. For ANECHOIC, it discovers Tools from the generated root `discover_tools` catalog and the current native MCP frontier. For other enabled MCP servers, it uses native discovery. It does not use a Workbench-only or hand-coded Tool allowlist or a unified Tool registry.

The Workbench streams Codex output and presents requested Tool interactions and approvals. It reuses the existing MCP Tools for queries, Views, saved items and service actions.

The conversation inherits the Workbench layout. Its placement, density, resizing and command-palette controls are not defined here.

This first integration does not provide a chat list, multiple conversations, a generic repository or code-editing agent, a separate Tool registry, a queue, scheduler, retry or rollback policy.
