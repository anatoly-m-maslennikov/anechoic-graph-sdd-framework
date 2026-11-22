---
atom_family: SPEC
atom_id: AN-S-1675
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: active
  version: 18
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Preserve Agentic Invocation results **without** replaying effects

## Claim

### Prose Claim


repeated delivery **or** reconnection for an Agentic Step Invocation.


the receiving context **must** report actual results against the identified Invocation. redelivery **or** reconnection **must not** imply permission **to** repeat already performed effects.
