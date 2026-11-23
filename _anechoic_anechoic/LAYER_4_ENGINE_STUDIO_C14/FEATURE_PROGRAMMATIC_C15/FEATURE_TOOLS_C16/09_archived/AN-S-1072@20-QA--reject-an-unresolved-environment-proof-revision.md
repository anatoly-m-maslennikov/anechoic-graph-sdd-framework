---
atom_family: SPEC
atom_id: AN-S-1072
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Reject an unresolved environment proof revision

# Reject an unresolved environment proof revision

## Test case

**Fixture:** leave one required environment revision unresolved **in** a proof frontier.

**Expected result:** fail with the stable incomplete-proof-frontier diagnostic **and** a non-zero exit.
