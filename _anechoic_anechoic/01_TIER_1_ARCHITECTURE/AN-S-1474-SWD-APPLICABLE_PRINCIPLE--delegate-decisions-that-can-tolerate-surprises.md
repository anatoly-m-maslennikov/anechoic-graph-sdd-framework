---
atom_family: SPEC
atom_id: AN-S-1474
concern:
  subject: Tolerance for unexpected delegated outcomes
  path: Design Foundations/Delegation and control
  relation: is_contained_by
container:
  component: C00
tier: 1
context:
  lens: SWD
  template: applicable_principle
state:
  status: "active"
  version: 6
  updated_at: "2026-11-27T13:00:59.913488+00:00"
relations:
  APPLIES:
  - AN-S-1473
  SERVES:
  - AN-S-1233
---

**P17**

## Summary

Delegate decisions that can tolerate surprises

## Claim

### Prose Claim

Let AI Agents make decisions where an unexpected result is acceptable.

## Details

### Examples

An Operator lets an AI Agent choose the order of independent documentation edits. Either order is acceptable, so the Agent can proceed without waiting for a decision.
