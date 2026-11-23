---
atom_family: SPEC
atom_id: AN-S-205
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

Reject missing relation target

# Reject missing relation target

## Test case

**Fixture:** point one relation at a nonexistent canonical filename stem.

**Expected result:** fail with the stable missing-relation-target diagnostic **and** a non-zero exit.
