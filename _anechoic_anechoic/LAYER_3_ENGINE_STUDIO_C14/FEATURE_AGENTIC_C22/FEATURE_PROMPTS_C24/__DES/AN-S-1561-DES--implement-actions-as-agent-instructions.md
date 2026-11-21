---
atom_family: SPEC
atom_id: AN-S-1561
structure:
  container:
    component: C24
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 15
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Implement Actions as Agent Instructions

## Claim

### Prose Claim

ACTION_PROMPTS **must** own self-contained agent-facing prompt implementations of methodology Actions. An ACTION_PROMPT supplies executable instructions **and** invocation context but does **not** own the Action meaning, Workflow state, Step transition, **or** Operator authority.
