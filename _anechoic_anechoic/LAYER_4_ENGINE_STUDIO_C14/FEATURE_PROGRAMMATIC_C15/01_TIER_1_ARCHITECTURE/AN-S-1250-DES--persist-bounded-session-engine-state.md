---
atom_family: SPEC
atom_id: AN-S-1250
container:
  component: C15
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 17
  updated_at: "2026-11-25T23:20:51.159798+00:00"
---
## Summary

Persist bounded session-engine state

## Claim

### Prose Claim

the framework **must** persist the minimum project-local session state required **to** resume routing **after** context compaction under `.anechoic_runtime`. Keep the active Project and routing context, applicable settings, and references needed to reload governing sources.

