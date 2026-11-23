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
  version: 7
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Preserve Agentic Invocation results **without** replaying effects

# Summary

Preserve Agentic Invocation results **without** replaying effects

## Scope

repeated delivery **or** reconnection for an Agentic Step Invocation.

## Claim

the receiving context **must** report actual results against the identified Invocation. redelivery **or** reconnection **must not** imply permission **to** repeat already performed effects.

## Details
