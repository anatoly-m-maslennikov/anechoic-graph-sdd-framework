---
atom_family: SPEC
atom_id: AN-S-1301
structure:
  container:
    component: C15
  tier: 4
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Separate action creation from provenance reliance

## Claim

### Prose Claim

An action may complete with observable pending Git/Journal provenance. That pending state is not reconciled, but Journal incompleteness alone does not gate its mutation, ordinary later work, promotion or release; retain detection of missing, unreachable, duplicate, mismatch and lag evidence.
