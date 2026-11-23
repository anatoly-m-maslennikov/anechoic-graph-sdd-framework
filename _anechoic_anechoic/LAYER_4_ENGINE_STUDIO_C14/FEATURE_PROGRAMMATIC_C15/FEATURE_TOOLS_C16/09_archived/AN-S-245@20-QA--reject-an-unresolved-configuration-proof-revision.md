---
atom_family: SPEC
atom_id: AN-S-245
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Reject an unresolved configuration proof revision

# Reject an unresolved configuration proof revision

## Test case

**Fixture:** leave one required configuration revision unresolved **in** a proof frontier.

**Expected result:** fail with the stable incomplete-proof-frontier diagnostic **and** a non-zero exit.
