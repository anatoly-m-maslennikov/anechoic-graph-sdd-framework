---
atom_family: SPEC
atom_id: AN-S-224
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-26 05:49:04 +0400
---
## Summary

Reject imprecise relation in strict scope

# Reject imprecise relation in strict scope

## Test case

**Fixture:** add an unadmitted imprecise relation kind as an operative relation
**in** a strict scope.

**Expected result:** fail with the stable imprecise-relation-in-strict-scope
diagnostic **and** a non-zero exit.
