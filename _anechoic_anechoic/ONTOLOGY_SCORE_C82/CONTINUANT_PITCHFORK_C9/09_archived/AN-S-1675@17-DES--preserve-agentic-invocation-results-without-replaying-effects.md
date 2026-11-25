---
atom_family: SPEC
atom_id: AN-S-1675
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 17
  updated_at: 2026-10-29 14:16:33 +0400
---
## Summary

Preserve Agentic Invocation results **without** replaying effects

## Claim scope

repeated delivery **or** reconnection for an Agentic Step Invocation.

## Claim

the receiving context **must** report actual results against the identified Invocation. redelivery **or** reconnection **must not** imply permission **to** repeat already performed effects.
