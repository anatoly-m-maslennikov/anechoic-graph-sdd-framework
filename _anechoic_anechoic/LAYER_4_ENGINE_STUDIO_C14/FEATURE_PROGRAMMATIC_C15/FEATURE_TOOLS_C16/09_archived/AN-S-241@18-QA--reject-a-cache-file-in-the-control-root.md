---
atom_family: SPEC
atom_id: AN-S-241
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

Reject a cache file in the control root

# Reject a cache file in the control root

## Test case

**Fixture:** add one cache file under the control root.

**Expected result:** fail with the stable non-governed-control-root-file diagnostic **and** a non-zero exit.
