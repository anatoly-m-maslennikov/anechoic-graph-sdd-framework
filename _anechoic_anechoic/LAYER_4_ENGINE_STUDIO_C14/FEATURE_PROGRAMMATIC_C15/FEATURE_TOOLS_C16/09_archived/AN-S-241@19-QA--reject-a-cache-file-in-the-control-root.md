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
  version: 19
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Reject a cache file in the control root

# Reject a cache file in the control root

## Test case

**Fixture:** add one cache file under the control root.

**Expected result:** fail with the stable non-governed-control-root-file diagnostic **and** a non-zero exit.
