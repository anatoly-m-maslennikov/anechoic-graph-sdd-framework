---
atom_family: SPEC
atom_id: AN-S-1065
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject unresolved revision

# Reject unresolved revision

## Test case

**Fixture:** bind provenance **to** an artifact revision that cannot be resolved exactly.

**Expected result:** fail with the stable unresolved-revision diagnostic **and** a non-zero exit.
