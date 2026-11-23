---
atom_family: SPEC
atom_id: AN-S-1061
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Return deterministic carrier diagnostics

# Return deterministic carrier diagnostics

## Test case

**Fixture:** run the malformed-filename fixture defined by CA-E-073 twice with the same settings **and** source frontier.

**Expected result:** return identical ordered diagnostics **and** exit status on both runs.
