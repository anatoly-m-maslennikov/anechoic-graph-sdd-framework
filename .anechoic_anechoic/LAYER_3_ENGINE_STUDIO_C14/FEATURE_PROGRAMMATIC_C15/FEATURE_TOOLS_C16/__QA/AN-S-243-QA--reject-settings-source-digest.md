---
atom_family: SPEC
atom_id: AN-S-243
structure:
  container:
    component: C16
  tier: 2
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject settings source digest

# Reject settings source digest

## Test case

**Fixture:** change one Project Settings source digest so it no longer matches the recorded source revision.

**Expected result:** fail with the stable settings-source-digest diagnostic **and** a non-zero exit.
