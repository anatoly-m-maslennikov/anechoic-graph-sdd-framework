---
atom_family: SPEC
atom_id: AN-S-1675
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: active
  version: 19
  updated_at: '2026-11-25T21:47:23.492699+00:00'
---
## Summary

Preserve Agentic Invocation results **without** replaying effects

## Claim

### Prose Claim


repeated delivery **or** reconnection for an Agentic Step Invocation.


the receiving context **must** report actual results against the identified Invocation. redelivery **or** reconnection **must not** imply permission **to** repeat already performed effects.
