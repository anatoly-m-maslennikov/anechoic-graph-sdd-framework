---
atom_family: SPEC
atom_id: AN-S-1511
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: active
  version: 23
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Reject unbounded production DEBUG logging

## Claim

### Prose Claim

Reject production DEBUG enabled globally without automatic expiry. Any enablement requires bounded component/subject/run/entity-or-equivalent scope and unchanged redaction.
