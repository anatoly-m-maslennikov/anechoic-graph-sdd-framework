---
atom_family: SPEC
atom_id: AN-S-1299
structure:
  container:
    component: C15
  tier: 4
context:
  lens: QA
state:
  status: active
  version: 21
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Reconcile a Journal-first action

## Claim

### Prose Claim

A Journal-first action remains `journal_recorded_git_pending` after exactly one canonical record binds one reachable real-change commit SHA until a later separate Git commit versions the Journal carrier containing that record. Verify pending before that carrier commit and `reconciled` after it; otherwise preserve pending and prohibit provenance reliance. The record does not embed the SHA of the commit containing itself.
