---
atom_family: TKT
atom_id: AN-T-3009
container:
  component: C43
priority: 2
context:
  template: task
  label: Epic
state:
  status: "backlog"
  version: 1
  updated_at: "2026-11-23T04:12:02.947926+00:00"
---
## Summary

Refactor Workbench Frontend and its API

## Objective

Make Workbench easier to change by simplifying the frontend and clarifying the Backend API it uses.

## Work

1. **Baseline.** Record the current API calls and behavior in standalone Workbench and the Codex MCP App. Cover query run and paging, saved SQL, Workspace and View changes, and common failure paths.
2. **Backend API.** Review the routes, request and response shapes, errors, and cancellation. Remove unused or duplicate endpoints after checking callers. Keep Project binding and query semantics in Backend and Kernel. Update the affected Contracts.
3. **Frontend.** Convert authored frontend code to strict TypeScript, including Svelte script blocks. Use one typed API boundary and one owner for each piece of client state. Reuse logic where the standalone and Codex surfaces need the same behavior.
4. **Components.** Review ownership and dependencies. Merge overlapping Components, promote Packages that need a Contract, demote Components whose behavior belongs with their owner, and create Components for distinct responsibilities. Update their Manifests and exact Spec Bindings.
5. **Verification.** Require zero forbidden imports in the affected Components and Packages, confirmed by the Realization Graph. Enforce 45 lines per function and 300 per Module. Add strict type checking to the static gate. Run contract and browser checks against the packaged runtime for both surfaces. Compare large-result behavior with the baseline.