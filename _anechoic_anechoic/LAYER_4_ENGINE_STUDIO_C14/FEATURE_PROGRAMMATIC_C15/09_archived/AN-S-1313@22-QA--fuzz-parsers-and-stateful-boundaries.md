---
atom_family: SPEC
atom_id: AN-S-1313
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Fuzz parsers and stateful boundaries

## Claim

### Prose Claim

A bounded property/state-machine campaign over valid, invalid and ordered cases preserves seed and minimal failing input/sequence. Explicitly accept or reject each defect; accepted defects gain deterministic regression. Reject unreplayable evidence and keep campaigns out of synchronous Hooks.
