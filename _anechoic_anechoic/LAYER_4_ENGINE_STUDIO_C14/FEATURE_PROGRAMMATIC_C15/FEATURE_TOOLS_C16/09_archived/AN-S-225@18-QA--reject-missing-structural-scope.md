---
atom_family: SPEC
atom_id: AN-S-225
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reject missing structural scope

# Reject missing structural scope

## Test case

**Fixture:** remove one structural-scope folder required by Project Settings.

**Expected result:** fail with the stable missing-structural-scope diagnostic **and** a non-zero exit.
