---
atom_family: SPEC
atom_id: AN-S-228
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

Reject an editor swap file in the control root

# Reject an editor swap file in the control root

## Test case

**Fixture:** add one editor swap file under the control root.

**Expected result:** fail with the stable non-governed-control-root-file diagnostic **and** a non-zero exit.
