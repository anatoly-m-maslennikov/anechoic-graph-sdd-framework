---
atom_family: SPEC
atom_id: AN-S-230
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reject settings source address

# Reject settings source address

## Test case

**Fixture:** change one Project Settings source address so it no longer resolves **to** the recorded source revision.

**Expected result:** fail with the stable settings-source-address diagnostic **and** a non-zero exit.
