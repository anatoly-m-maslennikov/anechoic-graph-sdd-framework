---
atom_family: SPEC
atom_id: AN-S-1439
container:
  component: C00
tier: 1
context:
  lens: SWD
  template: applicable_principle
state:
  status: "active"
  version: 5
  updated_at: "2026-11-27T11:25:47.555153+00:00"
relations:
  APPLIES:
  - AN-S-1484
  SERVES:
  - AN-S-1233
---

**P5**

## Summary

Work with the specification as a collection of Operators’ decisions

## Claim

### Prose Claim

Treat the Spec as a collection of decisions made by Operators or by AI Agents acting under their authority. Record every decision that matters to the Project, why it was made, and the facts and assumptions that mattered.

When a similar choice comes up, the AI Agent reads the Spec to recover the context. If the relevant conditions still hold, it can reuse the Operator’s decision.

## Details

### Examples

An Operator records a choice to use polling because a deployment cannot reliably deliver file change events. For the next watcher, an AI Agent checks that the same conditions hold and reuses the choice.
