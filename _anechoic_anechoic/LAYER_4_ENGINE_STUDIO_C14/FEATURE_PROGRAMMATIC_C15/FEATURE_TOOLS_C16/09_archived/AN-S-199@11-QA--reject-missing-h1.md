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
  version: 11
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Reject missing H1

# Reject missing H1

## Test case

**Fixture:** remove the first body H1.

**Expected result:** fail with the stable missing-H1 diagnostic **and** a non-zero exit.
