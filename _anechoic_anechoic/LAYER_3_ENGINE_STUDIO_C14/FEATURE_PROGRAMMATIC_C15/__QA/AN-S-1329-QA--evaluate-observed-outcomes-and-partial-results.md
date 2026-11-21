---
atom_family: SPEC
atom_id: AN-S-1329
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: active
  version: 17
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Evaluate observed outcomes and partial results

## Claim

### Prose Claim

Outcomes must distinguish complete, no-op, partial, failed, canceled and uncertain against durable effects. Partial reports completed data plus error without replay/remap; preserve required atomicity and mark unresolved when state cannot be distinguished.
