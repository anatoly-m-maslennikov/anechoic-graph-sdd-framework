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
  status: backlog
  version: 6
  updated_at: '2026-11-26T16:38:01.252157+00:00'

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
- Compile Tier 1 workflows directly in Python. Reuse the transition model
  for Mermaid and Lean.
- Compare one source-derived workflow with its Solution in Lean. Use
  Realization Graph identities and retain unresolved coverage.

## Acceptance

Verify one path that mutates state, one that only emits an output, and one
reachable path that does neither. Identify declared no-ops separately.
Leave unsupported translations or unobserved effects unresolved.

Trace a rebuild and a watched change to generation. Include the clock
trigger and recorded effects. Detect a repeated effect when outputs match.
