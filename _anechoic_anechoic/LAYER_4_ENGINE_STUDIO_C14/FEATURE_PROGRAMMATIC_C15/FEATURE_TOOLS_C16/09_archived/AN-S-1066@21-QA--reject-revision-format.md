---
atom_family: SPEC
atom_id: AN-S-1066
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Reject revision format

# Reject revision format

## Test case

**Fixture:** give one Atom an invalid version-and-timestamp revision format.

**Expected result:** fail with the stable revision-format diagnostic **and** a non-zero exit.
