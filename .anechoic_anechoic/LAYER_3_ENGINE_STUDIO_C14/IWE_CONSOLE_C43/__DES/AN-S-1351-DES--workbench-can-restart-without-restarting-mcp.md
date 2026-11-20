---
atom_family: SPEC
atom_id: AN-S-1351
structure:
  container:
    component: C43
  tier: 4
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Workbench can restart without restarting MCP

## Claim


### Prose Claim
Allow Operator/AI Agent to restart selected Project Workbench only through native `workbench_restart({})` or explicit health-page action. Restart closes old owner, rebuilds admitted Current/Draft sources and Current Scope Unit Declaration index, clears temporary result IDs, preserves sources/saved queries/Views and leaves MCP/unrelated services/container running. Return ready only after replacement is ready; invalid startup returns shared `workbench_unavailable` and stays unavailable until explicit restart—no retry, rollback or Business Journal event.

`workbench_restart({})` accepts no service/shell/container arguments and serializes with Project work, including cancellation, so no request uses a closed owner. Health GET stays read-only and available on failure; POST `/anechoic/health/workbench-restart` uses the same gateway, Project selection, blacklist and error boundary. Single Project body is empty; shared host requires exactly one `project_root` field and rejects unknown/repeated fields before effect. Render actual escaped ready/failure; add no picker, shell/Docker/JavaScript/query-editor control. Correcting an invalid Declaration alone does not restart Workbench.
