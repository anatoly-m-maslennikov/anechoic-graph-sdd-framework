---
atom_family: SPEC
atom_id: AN-S-1053
structure:
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

Reject malformed filename

# Reject malformed filename

## Test case

**Fixture:** remove one required segment from the canonical filename grammar.

**Expected result:** fail with the stable malformed-filename diagnostic **and** a non-zero exit.
