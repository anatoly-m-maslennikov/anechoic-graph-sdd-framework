---
atom_family: SPEC
atom_id: AN-S-1059
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

Reject ambiguous scalar

# Reject ambiguous scalar

## Test case

**Fixture:** encode one governed scalar with an ambiguous implicit YAML type.

**Expected result:** fail with the stable ambiguous-scalar diagnostic **and** a non-zero exit.
