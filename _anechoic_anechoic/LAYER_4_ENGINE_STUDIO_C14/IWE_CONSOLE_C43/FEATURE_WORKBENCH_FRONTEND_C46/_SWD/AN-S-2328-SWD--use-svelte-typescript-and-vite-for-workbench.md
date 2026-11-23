---
atom_family: SPEC
atom_id: AN-S-2328
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: "active"
  version: 10
  updated_at: "2026-11-23T04:35:26.541479+00:00"
---
## Summary

Use Svelte, TypeScript and Vite for Workbench

## Claim scope

The Workbench frontend.

## Claim

### Prose Claim

Build Svelte components and strict TypeScript with Vite. Run TypeScript and
Svelte type checks in the static phase.

Use the same typed Workbench API and browser state for standalone
Workbench and the Codex MCP App. The HTTP and MCP transports preserve
the Backend's public error code and operation result.

Keep SQL execution and result materialization in the Backend and Kernel.
Request bounded pages and use complete-result column metadata for display.
