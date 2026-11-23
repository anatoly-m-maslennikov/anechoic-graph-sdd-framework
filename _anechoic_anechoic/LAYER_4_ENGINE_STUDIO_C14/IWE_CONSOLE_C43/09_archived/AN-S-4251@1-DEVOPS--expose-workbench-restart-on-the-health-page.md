---
atom_family: SPEC
atom_id: AN-S-4251
container:
  component: C43
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 06:00:43 +0400
---

## Summary

Expose Workbench restart on the health page

## Claim

Show a Restart Workbench button on the HTML health page at `/anechoic/health`. Use a native HTML POST form to `/anechoic/health/workbench-restart`. On the Project server, its body is empty. On a shared host, require one `project_root` value, labelled Project folder. Reject unknown or repeated fields before any effect.

Route the action through the same gateway `workbench_restart` operation exposed by MCP, with the same Project selection, blacklist and public error boundary. Do not reimplement lifecycle control in the page. Show the ready or failure outcome as escaped text in the health view. Do not automatically repeat or restart another service.

GET health requests stay read-only. Preserve existing JSON readiness and HTML snapshot behavior. Keep the health page available when Workbench fails. The explicit action requires no separate approval form. It adds no generic service picker, shell commands, container control, JavaScript dependency or Workbench query-editor button.
