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
  version: 9
  updated_at: 2026-10-24 04:48:21 +0400
---
## Summary

Persist bounded session-engine state

# Persist bounded session-engine state

the framework **must** persist the minimum project-local session state required **to** resume routing **after** context compaction under `.anechoic_runtime`.
