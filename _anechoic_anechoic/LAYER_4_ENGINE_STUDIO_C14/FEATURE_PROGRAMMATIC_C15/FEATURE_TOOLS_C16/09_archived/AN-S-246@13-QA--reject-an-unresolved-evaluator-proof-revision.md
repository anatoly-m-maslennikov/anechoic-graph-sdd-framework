---
atom_family: SPEC
atom_id: AN-S-246
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

Reject an unresolved evaluator proof revision

# Reject an unresolved evaluator proof revision

## Test case

**Fixture:** leave one required evaluator revision unresolved **in** a proof frontier.

**Expected result:** fail with the stable incomplete-proof-frontier diagnostic **and** a non-zero exit.
