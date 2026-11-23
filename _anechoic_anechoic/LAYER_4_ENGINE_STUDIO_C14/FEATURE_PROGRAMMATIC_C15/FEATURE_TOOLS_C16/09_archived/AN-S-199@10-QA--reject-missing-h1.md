---
atom_family: SPEC
atom_id: AN-S-199
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-09-12 04:15:38 +0400
---
## Summary

Reject missing H1

# Reject missing H1

## Test case

**Fixture:** remove the first body H1.

**Expected result:** fail with the stable missing-H1 diagnostic **and** a non-zero exit.
