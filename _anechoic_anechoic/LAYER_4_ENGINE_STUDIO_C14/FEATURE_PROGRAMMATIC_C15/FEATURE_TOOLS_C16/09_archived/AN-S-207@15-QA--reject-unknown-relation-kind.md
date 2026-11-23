---
atom_family: SPEC
atom_id: AN-S-207
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Reject unknown relation kind

# Reject unknown relation kind

## Test case

**Fixture:** add one unregistered relation kind.

**Expected result:** fail with the stable unknown-relation-kind diagnostic **and** a non-zero exit.
