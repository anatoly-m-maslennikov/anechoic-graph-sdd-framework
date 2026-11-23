---
atom_family: SPEC
atom_id: AN-S-242
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Reject a backup file in the control root

# Reject a backup file in the control root

## Test case

**Fixture:** add one accidental backup file under the control root.

**Expected result:** fail with the stable non-governed-control-root-file diagnostic **and** a non-zero exit.
