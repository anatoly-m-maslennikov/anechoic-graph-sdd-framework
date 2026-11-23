---
atom_family: SPEC
atom_id: AN-S-243
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

Reject settings source digest

# Reject settings source digest

## Test case

**Fixture:** change one Project Settings source digest so it no longer matches the recorded source revision.

**Expected result:** fail with the stable settings-source-digest diagnostic **and** a non-zero exit.
