---
atom_family: SPEC
atom_id: AN-S-1335
container:
  component: C15
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Verify native Tool contract fidelity

## Claim

### Prose Claim

An active native Tool passes frontier contract fidelity only when its canonical structural request and result schemas, including definitions and required fields, and its decoded request/result payload meaning are preserved. Transport serialization differences are allowed only for a declared outer Project field such as project_root; no other transport-shape drift is introduced.

Verify names and descriptions against the configured code contracts as well as their canonical structural schemas.
