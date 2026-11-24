---
atom_family: SPEC
atom_id: AN-S-1319
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

Evaluate changed Python targets under one configuration

## Claim

### Prose Claim

Every changed Python target retains separate syntax, Ruff, Mypy and relevant behavioral evidence under one declared interpreter/configuration. A failed mechanism fails aggregate gate with target, diagnostic, boundary and replay command; no masking.
