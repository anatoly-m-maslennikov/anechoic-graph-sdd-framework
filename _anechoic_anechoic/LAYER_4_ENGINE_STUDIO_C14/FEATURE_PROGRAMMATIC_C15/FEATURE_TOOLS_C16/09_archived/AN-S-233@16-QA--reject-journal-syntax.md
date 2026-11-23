---
atom_family: SPEC
atom_id: AN-S-233
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 08:53:16 +0400
---
## Summary

Reject Journal syntax

# Reject Journal syntax

## Test case

**Fixture:** make one Work Journal line invalid NDJSON.

**Expected result:** fail with the stable Journal-syntax diagnostic **and** a non-zero exit.
