---
atom_family: SPEC
atom_id: AN-S-202
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

Reject empty Atom body

# Reject empty Atom body

## Test case

**Fixture:** remove the claim body below the H1.

**Expected result:** fail with the stable empty-Atom-body diagnostic **and** a non-zero exit.
