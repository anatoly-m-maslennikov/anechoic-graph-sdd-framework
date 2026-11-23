---
atom_family: SPEC
atom_id: AN-S-240
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

Reject a temporary file in the control root

# Reject a temporary file in the control root

## Test case

**Fixture:** add one temporary file under the control root.

**Expected result:** fail with the stable non-governed-control-root-file diagnostic **and** a non-zero exit.
