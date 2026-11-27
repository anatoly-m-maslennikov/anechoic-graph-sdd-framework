---
atom_family: SPEC
atom_id: AN-S-1561
concern:
  subject: "Prompt"
  path: "Model/Graph/Node//Artifact//SSOT//Realization/Content"
  relation: "is_contained_by"
container:
  component: C24
tier: 1
context:
  lens: DES
state:
  status: active
  version: 16
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Implement Actions as Agent Instructions

## Claim

### Prose Claim

ACTION_PROMPTS **must** own self-contained agent-facing prompt implementations of methodology Actions. An ACTION_PROMPT supplies executable instructions **and** invocation context but does **not** own the Action meaning, Workflow state, Step transition, **or** Operator authority.
