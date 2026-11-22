---
atom_family: TKT
atom_id: AN-T-2971
container:
  atom: AN-T-2935
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-22T00:05:13.848978+00:00"
---
## Summary

Return declared host Release commands through MCP

## Objective

Read the two Active Project Config claims. Return one shell-quoted host uv command per request. Preserve the existing Project gate and argument validation. Verify source selection, invalid claims, and command output without running a release.

## Done when

The native MCP entry points return the declared commands and reject missing or invalid definitions.
