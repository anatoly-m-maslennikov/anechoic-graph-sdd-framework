---
atom_family: SPEC
atom_id: AN-S-201
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

Reject summary H1 mismatch

# Reject summary H1 mismatch

## Test case

**Fixture:** change the H1 so it no longer faithfully renders the immutable filename summary.

**Expected result:** fail with the stable summary-H1-mismatch diagnostic **and** a non-zero exit.
