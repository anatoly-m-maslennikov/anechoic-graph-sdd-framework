---
atom_family: SPEC
atom_id: AN-S-1221
container:
  component: C48
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-11-21 12:36:57 +0400
---

## Summary

Exercise Workbench Workspace Views and Query Log

## Claim

### Prose Claim

Verify that a host-provided native session opens its isolated Workspace with at least one View for the explicit Project. Verify a read-only Workspace/View operation through the shared backend.

Verify native UI, standalone browser and MCP use the same Workspace/View effects. Separate native sessions must keep separate Workspaces and unsaved SQL. Verify no standalone chat, synthetic native session, magic Workflow, code runner, scheduler, or retry behavior is required.

In a disposable protocol host and disposable valid Project, verify that `workspace_open` alone exposes `ui://anechoic/workbench.html`; the compatibility probe remains separately linked; unknown resource URIs and unexpected inputs fail. Verify the resource is self-contained `text/html;profile=mcp-app` with no external script or stylesheet references, Workbench HTTP request, browser opening, or second server.

Verify native bootstrap accepts only the `workspace_open` host tool input's non-empty `session_id` and explicit `project_root` plus its initial structured result. Exercise either input/result arrival order, require the exact supplied IDs and initial Workspace, and verify no second `workspace_open` call occurs. For absent input or result, verify a binding error is shown and no backend call, URL/localStorage identity fallback, synthetic native session, or alternative Workspace selection occurs.

Through the native MCP transport, exercise every existing Workspace/View and query-log operation. Each call retains the exact `project_root`, uses one `tools/call`, preserves `structuredContent`, rejects `isError`, and reaches the shared handler. Check transport binding and error propagation without repeating the shared operation acceptance cases. Native mode must not apply standalone URL, localStorage or draft-migration behavior.

A disposable-host test proves protocol and application behavior only. The read-only probe separately verifies standard MCP Apps compatibility and must not be used as Workbench activation evidence.

Call the read-only `workbench_ui_probe` through the existing MCP connection. Verify its component renders in a compatible host, displays the initial host tool result, and reports a successful separate `workbench_ui_ping` bridge call. Verify resource and tools work over real MCP transport, reject unexpected arguments and unknown resource URIs, and do not start Workbench. Verify inline/fullscreen declaration, current and offered mode display, Expand only when fullscreen is available, accepted/inline-retained/rejected/unsupported results, actual returned-mode display, and no unavailable request.

Use a fixture whose directory basename differs from its declared Project name. Verify HTTP and MCP workspace_open/workspace_get return the declared project_name and the native Workbench header displays it. Workspace documents do not gain a persisted Project-name field. A native initial Workspace result missing project_name reports a binding error before further tool calls; no directory-basename fallback is used.
