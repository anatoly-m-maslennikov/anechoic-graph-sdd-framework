---
atom_family: SPEC
atom_id: AN-S-1071
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Reject an unresolved implementation proof revision

# Reject an unresolved implementation proof revision

## Test case

**Fixture:** leave one required implementation revision unresolved **in** a proof frontier.

**Expected result:** fail with the stable incomplete-proof-frontier diagnostic **and** a non-zero exit.
