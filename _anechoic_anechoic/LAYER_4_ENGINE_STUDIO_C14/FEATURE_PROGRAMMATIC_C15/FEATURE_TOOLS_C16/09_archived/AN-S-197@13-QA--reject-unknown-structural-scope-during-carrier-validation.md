---
atom_family: SPEC
atom_id: AN-S-197
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Reject unknown structural scope during carrier validation

# Reject unknown structural scope during carrier validation

## Test case

**Fixture:** place the Carrier under a non-Project Scope Unit absent from the owning Project's accepted Project Structure declarations. keep Project Settings valid for the Project root identity; a folder observation **or** Goal **must not** substitute for a missing declaration under CA-R-1483 **and** CA-R-1484.

**Expected result:** fail with the stable unknown-structural-scope diagnostic **and** a non-zero exit.
