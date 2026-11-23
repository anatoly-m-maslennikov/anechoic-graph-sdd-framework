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
  IS_REFERENCE:
  - AN-S-3323@2
  - AN-S-3361@2
  IS_SOLUTION_FOR:
  - AN-S-3182@11
state:
  status: active
  version: 1
  updated_at: '2026-11-22T23:52:17.262612+00:00'
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
claim as data. Compile its flat XState definition to one transition
model. Require disjoint event guards and a path to a final state from
every state. Guard success on a required effect when the evidence
shows that the effect is due.

Render Mermaid from that model. Check complete recorded trigger,
effect, and output sequences against it in Lean. Preserve passive
inputs and their causal links in the Flow Map. Use the same event
identities in the Solution and observed trace.
