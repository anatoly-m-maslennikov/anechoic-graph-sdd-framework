---
atom_family: SPEC
atom_id: AN-S-211
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Reject duplicate relation target

# Reject duplicate relation target

## Test case

**Fixture:** repeat one target inside a relation-kind list.

**Expected result:** fail with the stable duplicate-relation-target diagnostic **and** a non-zero exit.
