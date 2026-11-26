---
atom_family: SPEC
atom_id: AN-S-1671
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: active
  version: 22
  updated_at: '2026-11-25T21:47:22.821046+00:00'
---
## Summary

Provide self-contained Agentic Step Invocation payloads

## Claim

### Prose Claim


an executor dispatching **or** resuming an Agentic Step.


the executor **must** provide a self-contained Invocation sufficient for the receiving context **to** perform the admitted Action **without** remembering the Workflow procedure from earlier conversation.

- identify the Workflow Run **and** Step Run, exact admitted definition bindings, bound inputs **or** accessible references, relevant prior results **and** actual effects, applicable permissions, **and** required output.
- provide the instruction derived from the Action **and** its Step binding, including how **to** return the result **or** request missing input. the instruction is a derived presentation of governing authority, **not** another independently maintained procedure.
- an Integrated Invocation returns this context **and** instruction through the session interface; an Isolated Invocation supplies it **to** the separate context. no particular transport is required by this core rule.
