---
atom_family: SPEC
atom_id: AN-S-1067
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 08:53:16 +0400
---
## Summary

Reject an unresolved artifact proof revision

# Reject an unresolved artifact proof revision

## Test case

**Fixture:** leave one required artifact revision unresolved **in** a proof frontier.

**Expected result:** fail with the stable incomplete-proof-frontier diagnostic **and** a non-zero exit.
