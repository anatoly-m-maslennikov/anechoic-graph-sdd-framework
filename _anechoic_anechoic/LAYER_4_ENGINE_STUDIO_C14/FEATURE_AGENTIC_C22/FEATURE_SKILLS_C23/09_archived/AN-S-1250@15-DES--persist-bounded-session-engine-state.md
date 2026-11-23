---
atom_family: SPEC
atom_id: AN-S-1250
container:
  component: C23
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Persist bounded session-engine state

## Claim

### Prose Claim

the framework **must** persist the minimum project-local session state required **to** resume routing **after** context compaction under `.anechoic_runtime`.
