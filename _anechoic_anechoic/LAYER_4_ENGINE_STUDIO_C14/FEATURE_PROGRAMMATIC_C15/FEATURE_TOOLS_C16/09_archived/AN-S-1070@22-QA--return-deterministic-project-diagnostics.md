---
atom_family: SPEC
atom_id: AN-S-1070
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Return deterministic project diagnostics

# Return deterministic project diagnostics

## Test case

**Fixture:** run the missing-relation-target fixture defined by CA-E-104 twice with the same settings **and** source frontier.

**Expected result:** return identical ordered diagnostics **and** exit status on both runs.
