---
atom_family: SPEC
atom_id: AN-S-1073
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 17:04:05 +0400
---
## Summary

Reject an unresolved material-input proof revision

# Reject an unresolved material-input proof revision

## Test case

**Fixture:** leave one required material-input revision unresolved **in** a proof frontier.

**Expected result:** fail with the stable incomplete-proof-frontier diagnostic **and** a non-zero exit.
