---
atom_family: SPEC
atom_id: AN-S-4430
container:
  component: C15
tier: 1
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 12:28:12 +0400
---
## Summary

Persist bounded session-engine state

## Claim



### Prose Claim
the framework **must** persist the minimum project-local session state required **to** resume routing **after** context compaction under `.anechoic_runtime`.
