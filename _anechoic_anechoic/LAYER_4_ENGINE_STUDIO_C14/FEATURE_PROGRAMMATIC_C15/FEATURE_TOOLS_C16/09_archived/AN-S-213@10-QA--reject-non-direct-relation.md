---
atom_family: SPEC
atom_id: AN-S-213
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

Reject non direct relation

# Reject non direct relation

## Test case

**Fixture:** persist a transitive semantic edge **in** addition **to** the direct path that already entails it.

**Expected result:** fail with the stable non-direct-relation diagnostic **and** a non-zero exit.
