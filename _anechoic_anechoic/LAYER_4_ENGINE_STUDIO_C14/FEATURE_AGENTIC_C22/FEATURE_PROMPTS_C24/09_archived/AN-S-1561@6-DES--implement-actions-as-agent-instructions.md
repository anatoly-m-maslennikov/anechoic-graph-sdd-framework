---
atom_family: SPEC
atom_id: AN-S-1561
container:
  component: C24
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 01:28:26 +0400
---
## Summary

Implement Actions as Agent Instructions

# Implement Actions as Agent Instructions

ACTION_PROMPTS **must** own self-contained agent-facing prompt implementations of methodology Actions. An ACTION_PROMPT supplies executable instructions **and** invocation context but does **not** own the Action meaning, Workflow state, Step transition, **or** Operator authority.
