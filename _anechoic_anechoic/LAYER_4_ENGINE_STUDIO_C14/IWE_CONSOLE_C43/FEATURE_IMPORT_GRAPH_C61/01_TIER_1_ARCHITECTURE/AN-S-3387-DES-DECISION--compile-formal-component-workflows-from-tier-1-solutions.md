---
atom_family: SPEC
atom_id: AN-S-3387
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3182@11
state:
  status: "active"
  version: 2
  updated_at: "2026-11-26T16:43:14.630683+00:00"
---

## Summary

Compile formal Component workflows from Tier 1 Solutions

## Claim

### Prose Claim

Put observable inputs, outputs, and promised effects in the Tier 0
Contract. Describe the internal flow in a Tier 1 Solution linked by
`IS_SOLUTION_FOR`. The Manifest declares client and server interfaces
and state access. A Solution covers one bounded Action for a Component
or Component Seed. Name the input or clock event that triggers it.

Read a literal Python `component_workflow(component, action, machine)`
claim as data. Python validates and normalizes its flat transition
graph. Require disjoint event guards and a path to a final state from
every state. Guard success on a required effect when it is due.

Render Mermaid from that model. Check complete recorded trigger,
effect, and output sequences against it in Lean. Preserve passive
inputs and their causal links in the Flow Map. Use the same event
identities in the Solution and observed trace.

For a source-derived comparison, reuse Realization Graph Code Units and
call edges. Lower supported source branches, effects, and outputs to
the same event vocabulary. In Lean, check that each supported realized
execution is allowed by the Solution. Mark incomplete source coverage
unresolved and retain the observed-run check.
