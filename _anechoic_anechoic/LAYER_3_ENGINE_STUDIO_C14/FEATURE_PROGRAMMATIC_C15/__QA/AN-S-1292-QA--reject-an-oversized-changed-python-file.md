---
atom_family: SPEC
atom_id: AN-S-1292
structure:
  container:
    component: C15
  tier: 6
context:
  lens: QA
state:
  status: active
  version: 23
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Reject an oversized changed Python file

## Claim

### Prose Claim

Reject a new or materially changed hand-authored Python file over 200 physical lines unless a specific bounded exception applies; remediation is reduce, split by responsibility, or supply that exception.
