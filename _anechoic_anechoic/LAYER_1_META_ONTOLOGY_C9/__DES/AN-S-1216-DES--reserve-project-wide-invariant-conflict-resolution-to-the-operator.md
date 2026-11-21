---
atom_family: SPEC
atom_id: AN-S-1216
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Reserve Project-wide invariant conflict resolution to the Operator

## Claim

### Prose Claim


conflicts between active Project-wide foundational invariants **and** an AI Agent's delegated conflict resolution.


- **only** an Operator **may** resolve a conflict between active Project-wide foundational invariants, **and** an Operator's decision to resolve that conflict is non-delegable.
- an AI Agent **may** detect, analyze, **and** propose resolutions for a conflict between active Project-wide foundational invariants but **must not** choose a resolution for a conflict between active Project-wide foundational invariants.
- an AI Agent **may** resolve a conflict that does **not** involve two active Project-wide foundational invariants **only** **when** the AI Agent's active Operator delegation permits **every** required action **and** the configured confidence requirements are satisfied.
