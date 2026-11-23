---
atom_family: SPEC
atom_id: AN-S-1053
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Reject malformed filename

# Reject malformed filename

## Test case

**Fixture:** remove one required segment from the canonical filename grammar.

**Expected result:** fail with the stable malformed-filename diagnostic **and** a non-zero exit.
