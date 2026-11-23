---
atom_family: SPEC
atom_id: AN-S-211
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

Reject duplicate relation target

# Reject duplicate relation target

## Test case

**Fixture:** repeat one target inside a relation-kind list.

**Expected result:** fail with the stable duplicate-relation-target diagnostic **and** a non-zero exit.
