---
atom_family: SPEC
atom_id: AN-S-202
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject empty Atom body

# Reject empty Atom body

## Test case

**Fixture:** remove the claim body below the H1.

**Expected result:** fail with the stable empty-Atom-body diagnostic **and** a non-zero exit.
