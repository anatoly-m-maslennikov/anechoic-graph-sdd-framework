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
  version: 19
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Reject settings source digest

# Reject settings source digest

## Test case

**Fixture:** change one Project Settings source digest so it no longer matches the recorded source revision.

**Expected result:** fail with the stable settings-source-digest diagnostic **and** a non-zero exit.
