---
atom_family: TKT
atom_id: AN-T-2973
container:
  component: C61
priority: 2
context:
  template: task
  label: Epic
state:
  status: archived
  version: 3
  updated_at: '2026-11-22T21:23:44.851697+00:00'
relations:
  IS_REFERENCE:
  - AN-S-3187@1-draft
  - AN-S-3188@1-draft
  - AN-S-3189@1-draft
  - AN-S-3361@1
---
## Summary

Detect state mutations and silent dead ends with Lean

## Objective

Track mutations on reachable code paths. Report a dead end when an action
handles an input or event and makes zero tracked state mutations and produces
zero observable output.

## Work

- Check state mutations and shared-state access under `boundaries.state`.
  Apply `pure`, default `local`, and named channel grants `r`, `w`, and `rw`.
- Reuse the Autoform state pilot. Model the action, state owner, mutation
  trace, and observed outputs in Lean.
- Count results, errors, emitted events, and external outputs at the
  selected boundary. Capture writes even when they restore the starting value.
- Compare the Lean result with runtime evidence. Show the path, source
  location, and a concrete input for each confirmed dead end.
- Publish mutation and dead-end findings in the Realization Graph.

- Map Component inputs, trigger conditions, Actions, outputs, and side
  effects. Observe generation in the Orchestrator and compare streams in Lean.

## Acceptance

Verify one path that mutates state, one that only emits an output, and one
reachable path that does neither. Identify declared no-ops separately.
Leave unsupported translations or unobserved effects unresolved.

Trace a rebuild and a watched change to generation. Include the clock
trigger and recorded effects. Detect a repeated effect when outputs match.
