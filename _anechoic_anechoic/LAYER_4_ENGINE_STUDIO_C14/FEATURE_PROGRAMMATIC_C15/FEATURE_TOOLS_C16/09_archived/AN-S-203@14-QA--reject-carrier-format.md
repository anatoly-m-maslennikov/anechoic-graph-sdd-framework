---
atom_family: SPEC
atom_id: AN-S-203
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

Reject carrier format

# Reject carrier format

## Test case

**Fixture:** change the carrier extension **to** one **not** registered for its Artifact form.

**Expected result:** fail with the stable carrier-format diagnostic **and** a non-zero exit.
