---
atom_family: SPEC
atom_id: AN-S-228
structure:
  container:
    component: C16
  tier: 2
context:
  lens: QA
state:
  status: active
  version: 21
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject an editor swap file in the control root

# Reject an editor swap file in the control root

## Test case

**Fixture:** add one editor swap file under the control root.

**Expected result:** fail with the stable non-governed-control-root-file diagnostic **and** a non-zero exit.
