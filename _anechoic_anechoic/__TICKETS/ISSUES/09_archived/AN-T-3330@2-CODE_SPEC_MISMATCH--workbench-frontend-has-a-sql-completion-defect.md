---
atom_family: TKT
atom_id: AN-T-3330
container:
  component: C46
priority: 2
context:
  template: code_spec_mismatch
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 22:57:19 +0400
---

## Summary

Workbench Frontend has a SQL completion defect

## Claim

### Prose Claim

The inspected Svelte frontend uses shared Workspace transports, CodeMirror and Tabulator. Its custom completion replaces a qualified column’s prefix and inserts status text without escaping apostrophes.

**Code locations and review notes**

[SqlEditor.svelte](../../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src/lib/SqlEditor.svelte) builds quoted-column completion options, then replaces the complete matched token using only the column text. Its status completion appends raw values and a closing quote.

[App.svelte](../../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src/App.svelte) coordinates View state, Run/Check, result paging, autosave and commands. [ResultsTable.svelte](../../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src/lib/ResultsTable.svelte) renders the read-only Tabulator grid. [mcp_app_transport.ts](../../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src/lib/mcp_app_transport.ts) binds the shared App through the native bridge.

Inspection on 9 November 2026, current working tree. The workspace tests (18 cases) and focused editor-helper test (one case) passed in this review. Minimal reproductions confirmed both completion defects; the passing tests do not cover them. Browser E2E, TypeScript checks, standalone build, inline MCP artifact checks and native or visual acceptance were not rerun in this review.

App.svelte has 350 total lines in the inspected state.
