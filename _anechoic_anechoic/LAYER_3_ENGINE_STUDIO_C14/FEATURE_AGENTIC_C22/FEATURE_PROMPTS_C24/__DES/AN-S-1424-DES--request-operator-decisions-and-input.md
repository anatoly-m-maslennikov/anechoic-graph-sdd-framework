---
atom_family: SPEC
atom_id: AN-S-1424
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

Request Operator Decisions and Input

## Claim

### Prose Claim

OPERATOR_PROMPTS **must** own user-facing prompts that request an Operator decision, authorization, clarification, **or** input. They **must not** be treated as agent-executable Action implementations **or** as substitutes for the Operator's response.
