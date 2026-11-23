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
  version: 20
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Reject malformed filename

# Reject malformed filename

## Test case

**Fixture:** remove one required segment from the canonical filename grammar.

**Expected result:** fail with the stable malformed-filename diagnostic **and** a non-zero exit.
