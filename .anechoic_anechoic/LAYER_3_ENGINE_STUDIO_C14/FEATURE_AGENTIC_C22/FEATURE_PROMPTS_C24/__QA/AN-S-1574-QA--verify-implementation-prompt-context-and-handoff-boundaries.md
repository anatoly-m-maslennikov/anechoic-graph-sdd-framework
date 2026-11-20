---
atom_family: SPEC
atom_id: AN-S-1574
structure:
  container:
    component: C24
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 14
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Verify implementation prompt context and handoff boundaries

## Claim

### Prose Claim

the Implementation passes this Evaluation only when each actual Agentic dispatch uses its supplied Step context, and an Isolated dispatch has a complete under-fifteen-minute subtask handoff and fresh admission.

## Details

### Scope

Integrated and Isolated prompt invocation and return behavior.

Missing context blocks. The returned result cannot auto-dispatch a successor, alter Workflow state, or claim that the caller accepted its handoff.
