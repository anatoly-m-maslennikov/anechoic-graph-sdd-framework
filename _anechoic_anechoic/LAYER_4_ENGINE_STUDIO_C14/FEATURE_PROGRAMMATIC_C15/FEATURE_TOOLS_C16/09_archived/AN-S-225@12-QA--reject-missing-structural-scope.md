---
atom_family: SPEC
atom_id: AN-S-225
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

Reject missing structural scope

# Reject missing structural scope

## Test case

**Fixture:** remove one structural-scope folder required by Project Settings.

**Expected result:** fail with the stable missing-structural-scope diagnostic **and** a non-zero exit.
