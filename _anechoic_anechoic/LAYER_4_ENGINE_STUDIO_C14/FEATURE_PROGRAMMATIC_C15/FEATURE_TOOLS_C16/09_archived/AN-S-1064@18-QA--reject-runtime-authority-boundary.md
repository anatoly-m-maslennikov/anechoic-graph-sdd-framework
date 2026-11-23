---
atom_family: SPEC
atom_id: AN-S-1064
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reject runtime authority boundary

# Reject runtime authority boundary

## Test case

**Fixture:** place the **only** authoritative copy of one active Atom under `.anechoic_runtime`.

**Expected result:** fail with the stable runtime-authority-boundary diagnostic **and** a non-zero exit.
