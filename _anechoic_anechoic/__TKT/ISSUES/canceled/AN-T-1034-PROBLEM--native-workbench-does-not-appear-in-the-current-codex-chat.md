---
atom_family: TKT
atom_id: AN-T-1034
structure:
  container:
    component: C48
  priority: 2
context:
  template: problem
state:
  status: "canceled"
  version: 2
  updated_at: "2026-11-21T08:40:27.028146+00:00"
---

## Summary

Native Workbench does not appear in the current Codex chat

## Concern

The Operator sees no Workbench interface after `workspace_open` in this Codex chat. The call returns the correct Workspace and declared Project name.

The released MCP advertises `ui://anechoic/workbench.html` and serves the current self-contained artifact with MIME `text/html;profile=mcp-app`. The application bridge passes disposable-host tests. These checks do not prove that Codex mounts the UI.

## Evidence

The live descriptor and resource check is recorded in the CA-P-2710 release acceptance report. The Operator confirmed that nothing appeared. Computer Use cannot inspect Codex's own window.

Calls in this chat are exposed through `functions.exec`. That call path may explain the missing UI, but this is an inference. Neither a host limitation nor a cache fault has been established. No documented direct rendering action is available in this session.

## Impact

The released backend and browser Workbench work, but native Codex UI delivery does not meet CA-R-2902 yet. Native-host acceptance remains open.

## Disposition

The Operator moved to BB and retired the repository-local Codex plugin.
