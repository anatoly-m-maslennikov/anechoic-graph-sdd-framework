---
identity:
  atom_id: AN-S-1300
context:
  container:
    component: C15
  tier: 4
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Reject duplicate or mismatched provenance bindings

## Claim

### Prose Claim

Block reconciliation when canonical records or real-change commits duplicate, or revision/digest mismatch. Report the discrepancy without guessing a record; require deterministic repair to one binding.
