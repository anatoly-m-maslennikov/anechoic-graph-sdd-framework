---
atom_family: SPEC
atom_id: AN-S-3361
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3083@6
  - AN-S-3339@16
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T21:23:44.851697+00:00'
---

## Summary

Map Component flows and compare observable streams

## Claim

### Prose Claim

Declare typed inputs, trigger conditions, Actions, outputs, and side effects.
Map declarations to Code Units. A clock event can satisfy a trigger condition.
State changes are side effects.

Record observed streams at the Component boundary. Keep event identity,
causal order, outcome, and effect target. Publish the map and streams in
the Beta SQL interface. Start with Orchestrator generation.

Find shared paths in the graph. Use an LLM to suggest comparable paths.
Use Lean to compare outputs and effects for aligned, complete evidence.
Keep incomplete observations unresolved and review candidates before merging.
