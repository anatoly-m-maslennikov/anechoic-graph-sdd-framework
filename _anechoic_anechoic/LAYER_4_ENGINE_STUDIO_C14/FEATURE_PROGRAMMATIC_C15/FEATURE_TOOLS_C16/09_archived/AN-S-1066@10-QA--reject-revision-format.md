---
atom_family: SPEC
atom_id: AN-S-1066
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

Reject revision format

# Reject revision format

## Test case

**Fixture:** give one Atom an invalid version-and-timestamp revision format.

**Expected result:** fail with the stable revision-format diagnostic **and** a non-zero exit.
