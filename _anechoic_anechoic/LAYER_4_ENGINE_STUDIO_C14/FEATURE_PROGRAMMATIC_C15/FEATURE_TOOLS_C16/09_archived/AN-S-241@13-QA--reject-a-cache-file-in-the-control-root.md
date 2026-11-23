---
atom_family: SPEC
atom_id: AN-S-241
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Reject a cache file in the control root

# Reject a cache file in the control root

## Test case

**Fixture:** add one cache file under the control root.

**Expected result:** fail with the stable non-governed-control-root-file diagnostic **and** a non-zero exit.
