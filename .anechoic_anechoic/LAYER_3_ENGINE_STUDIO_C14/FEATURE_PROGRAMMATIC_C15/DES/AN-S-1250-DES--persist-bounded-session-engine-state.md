---
identity:
  atom_id: AN-S-1250
context:
  container:
    component: C15
  tier: 1
  lens: DES
state:
  status: active
  version: 16
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Persist bounded session-engine state

## Claim

### Prose Claim

the framework **must** persist the minimum project-local session state required **to** resume routing **after** context compaction under `.anechoic_runtime`.

