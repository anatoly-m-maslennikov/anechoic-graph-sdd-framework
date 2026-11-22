---
atom_family: TKT
atom_id: AN-T-2954
container:
  atom: AN-T-2973
priority: 2
context:
  template: task
state:
  status: "done"
  version: 4
  updated_at: "2026-11-22T16:55:34.701567+00:00"
---
## Summary

Publish State Analyzer findings in the Realization Graph

## Work

Reuse source discovery, watcher, and DuckDB projection. Publish source-backed state and dead-end findings against existing Module and Package nodes in Workbench, Console, and MCP. Use the same findings for lint.

## Acceptance

A changed source or grant refreshes affected findings. Lint blocks confirmed violations and reports unresolved effects separately.

Retain the source location, concrete input, and effect evidence for each dead end.

## Implementation evidence

- Both Realization Graph paths publish `state_effect_findings`, with ordered events, source locations, and concrete inputs for witnessed actions.
- Local verification covered Lean findings through MCP, a watched channel grant change, targeted rebuild, and retained database admission.
- Static lint blocks confirmed denied access and undeclared dead ends. Missing Lean or unsupported effects remain unresolved.
