---
atom_family: SPEC
atom_id: AN-S-233
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Reject Journal syntax

# Reject Journal syntax

## Test case

**Fixture:** make one Work Journal line invalid NDJSON.

**Expected result:** fail with the stable Journal-syntax diagnostic **and** a non-zero exit.
