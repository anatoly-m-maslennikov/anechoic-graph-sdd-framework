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
  status: active
  version: 2
  updated_at: '2026-11-22T21:50:23.939618+00:00'
---

## Summary

Map Component flows and compare observable streams

## Claim

### Prose Claim

Declare I/O interfaces and state access at their Component boundaries.
Record trigger conditions and Actions as Component behavior. A clock
event can satisfy a trigger. State changes are side effects.

Record observed streams at the Component boundary. Keep event identity,
causal links, outcome, and effect target. Derive the Flow Map from
observations and link Code Units when source evidence is available.
Publish the map and streams in Beta SQL.

Find shared paths in the graph. Use an LLM to suggest comparable paths.
Use Lean to compare outputs and effects for aligned, complete evidence.
Keep incomplete observations unresolved and review candidates before merging.
