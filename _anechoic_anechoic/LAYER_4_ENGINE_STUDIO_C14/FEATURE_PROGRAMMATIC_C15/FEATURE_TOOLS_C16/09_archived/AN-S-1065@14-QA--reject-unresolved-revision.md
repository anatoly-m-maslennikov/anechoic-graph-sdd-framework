---
atom_family: SPEC
atom_id: AN-S-1065
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

Reject unresolved revision

# Reject unresolved revision

## Test case

**Fixture:** bind provenance **to** an artifact revision that cannot be resolved exactly.

**Expected result:** fail with the stable unresolved-revision diagnostic **and** a non-zero exit.
