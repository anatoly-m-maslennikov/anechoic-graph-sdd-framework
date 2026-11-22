---
atom_family: SPEC
atom_id: AN-S-216
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject downstream parent

# Reject downstream parent

## Test case

**Fixture:** point a tier-classified RMED child at a parent with a greater global tier number.

**Expected result:** fail with the stable downstream-parent diagnostic **and** a non-zero exit.
