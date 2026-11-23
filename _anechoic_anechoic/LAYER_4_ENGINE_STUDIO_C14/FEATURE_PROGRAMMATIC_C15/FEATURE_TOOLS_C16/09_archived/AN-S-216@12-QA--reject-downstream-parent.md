---
atom_family: SPEC
atom_id: AN-S-216
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reject downstream parent

# Reject downstream parent

## Test case

**Fixture:** point a tier-classified RMED child at a parent with a greater global tier number.

**Expected result:** fail with the stable downstream-parent diagnostic **and** a non-zero exit.
