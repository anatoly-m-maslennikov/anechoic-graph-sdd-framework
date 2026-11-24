---
atom_family: SPEC
atom_id: AN-S-205
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject missing relation target

# Reject missing relation target

## Test case

**Fixture:** point one relation at a nonexistent canonical filename stem.

**Expected result:** fail with the stable missing-relation-target diagnostic **and** a non-zero exit.
