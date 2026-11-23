---
atom_family: SPEC
atom_id: AN-S-243
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

Reject settings source digest

# Reject settings source digest

## Test case

**Fixture:** change one Project Settings source digest so it no longer matches the recorded source revision.

**Expected result:** fail with the stable settings-source-digest diagnostic **and** a non-zero exit.
