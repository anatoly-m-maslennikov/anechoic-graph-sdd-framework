---
atom_family: SPEC
atom_id: AN-S-1059
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

Reject ambiguous scalar

# Reject ambiguous scalar

## Test case

**Fixture:** encode one governed scalar with an ambiguous implicit YAML type.

**Expected result:** fail with the stable ambiguous-scalar diagnostic **and** a non-zero exit.
