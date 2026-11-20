---
identity:
  atom_id: AN-S-1318
context:
  container:
    component: C15
  tier: 6
  lens: QA
state:
  status: active
  version: 24
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify changed Python with Ruff

## Claim

### Prose Claim

Pinned Ruff format, lint and complexity profile must report a changed unit above configured `C901`; reject it unless a bounded exception records rule, value, reason and review condition.
