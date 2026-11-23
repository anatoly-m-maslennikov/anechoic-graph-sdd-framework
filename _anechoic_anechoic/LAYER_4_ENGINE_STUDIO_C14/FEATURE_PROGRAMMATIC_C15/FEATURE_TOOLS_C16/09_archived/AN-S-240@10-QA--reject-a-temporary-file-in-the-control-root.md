---
atom_family: SPEC
atom_id: AN-S-240
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

Reject a temporary file in the control root

# Reject a temporary file in the control root

## Test case

**Fixture:** add one temporary file under the control root.

**Expected result:** fail with the stable non-governed-control-root-file diagnostic **and** a non-zero exit.
