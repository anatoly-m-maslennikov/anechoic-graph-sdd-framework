---
atom_family: SPEC
atom_id: AN-S-1310
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: active
  version: 21
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Evaluate diagnostic log contracts

## Claim

### Prose Claim

Across normal, recoverable abnormal, failed and DEBUG diagnostics, require timestamp, level, component, operation, outcome and available action identity; enforce Logging Policy levels, redaction and separation from Journal meaning. Reject schema, level or redaction defects.
